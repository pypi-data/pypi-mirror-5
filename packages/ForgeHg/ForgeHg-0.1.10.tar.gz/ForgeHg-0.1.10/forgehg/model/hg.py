import os
import re
import shutil
import logging
from binascii import b2a_hex
from datetime import datetime
from cStringIO import StringIO
from ConfigParser import ConfigParser
from itertools import islice
from shutil import rmtree

import tg
from pylons import app_globals as g
os.environ['HGRCPATH'] = '' # disable loading .hgrc
from mercurial import ui, hg, cmdutil, commands
from mercurial.error import RepoLookupError

from pymongo.errors import DuplicateKeyError

from ming.base import Object
from ming.orm import Mapper, session
from ming.utils import LazyProperty

from allura import model as M
from allura.lib import helpers as h
from allura.model.repository import topological_sort, GitLikeTree, zipdir

log = logging.getLogger(__name__)

class Repository(M.Repository):
    tool_name='Hg'
    repo_id='hg'
    type_s='Hg Repository'
    class __mongometa__:
        name='hg-repository'

    @LazyProperty
    def _impl(self):
        return HgImplementation(self)

    def merge_command(self, merge_request):
        '''Return the command to merge a given commit into a given target branch'''
        return 'hg checkout %s\nhg pull -r %s %s' % (
            merge_request.target_branch,
            merge_request.downstream.commit_id,
            merge_request.downstream_repo_url,
        )

    def count(self, branch='default'):
        return super(Repository, self).count(branch)

    def log(self, branch='default', offset=0, limit=10):
        return super(Repository, self).log(branch, offset, limit)

class HgUI(ui.ui):
    '''Hg UI subclass that suppresses reporting of untrusted hgrc files.'''
    def __init__(self, *args, **kwargs):
        super(HgUI, self).__init__(*args, **kwargs)
        self._reportuntrusted = False

class HgImplementation(M.RepositoryImplementation):
    re_hg_user = re.compile('(.*) <(.*)>')

    def __init__(self, repo):
        self._repo = repo

    @LazyProperty
    def _hg(self):
        try:
            return hg.repository(HgUI(), self._repo.full_fs_path)
        except hg.error.RepoError as e:
            log.error('Error looking up repo at %s: %s',
                    self._repo.full_fs_path, e)
            return None

    def init(self):
        fullname = self._setup_paths()
        log.info('hg init %s', fullname)
        if os.path.exists(fullname):
            shutil.rmtree(fullname)
        repo = hg.repository(
            ui.ui(), self._repo.full_fs_path, create=True)
        self.__dict__['_hg'] = repo
        self._setup_special_files()
        self._repo.status = 'ready'

    def clone_from(self, source_url):
        '''Initialize a repo as a clone of another'''
        self._repo.status = 'cloning'
        session(self._repo).flush(self._repo)
        log.info('Initialize %r as a clone of %s',
                 self._repo, source_url)
        try:
            fullname = self._setup_paths(create_repo_dir=False)
            if os.path.exists(fullname):
                shutil.rmtree(fullname)
            # !$ hg doesn't like unicode as urls
            src, repo = hg.clone(
                ui.ui(),
                source_url.encode('utf-8'),
                self._repo.full_fs_path.encode('utf-8'),
                update=False)
            self.__dict__['_hg'] = repo
            self._setup_special_files(source_url)
        except:
            self._repo.status = 'ready'
            session(self._repo).flush(self._repo)
            raise

    def commit(self, rev):
        '''Return a Commit object.  rev can be _id or a branch/tag name'''
        # See if the rev is a named ref that we have cached, and use the sha1
        # from the cache. This ensures that we don't return a sha1 that we
        # don't have indexed into mongo yet.
        for ref in self._repo.heads + self._repo.branches + self._repo.repo_tags:
            if ref.name == rev:
                rev = ref.object_id
                break
        result = M.repo.Commit.query.get(_id=rev)
        if result is None:
            try:
                impl = self._hg[str(rev)]
                result = M.repo.Commit.query.get(_id=impl.hex())
            except Exception, e:
                log.exception(e)
        if result is None: return None
        result.set_context(self._repo)
        return result

    def real_parents(self, ci):
        """Return all parents of a commit, excluding the 'null revision' (a
        fake revision added as the parent of the root commit by the Hg api).
        """
        return [p for p in ci.parents() if p]

    def all_commit_ids(self):
        """Return a list of commit ids, starting with the head(s) and ending
        with the root (first commit) of the tree.
        """
        graph = {}
        to_visit = [ self._hg[hd] for hd in self._hg.heads() ]
        while to_visit:
            obj = to_visit.pop()
            if obj.hex() in graph: continue
            parents = self.real_parents(obj)
            graph[obj.hex()] = set(
                p.hex() for p in parents
                if p.hex() != obj.hex())
            to_visit += parents
        return reversed([ ci for ci in topological_sort(graph) ])

    def new_commits(self, all_commits=False):
        graph = {}
        to_visit = [ self._hg[hd] for hd in self._hg.heads() ]
        while to_visit:
            obj = to_visit.pop()
            if obj.hex() in graph: continue
            if not all_commits:
                # Look up the object
                if M.repo.Commit.query.find(dict(_id=obj.hex())).count():
                    graph[obj.hex()] = set() # mark as parentless
                    continue
            parents = self.real_parents(obj)
            graph[obj.hex()] = set(
                p.hex() for p in parents
                if p.hex() != obj.hex())
            to_visit += parents
        return list(topological_sort(graph))

    def refresh_heads(self):
        self._repo.heads = [
            Object(name=None, object_id=self._hg[head].hex())
            for head in self._hg.heads()]

        self._repo.branches = []
        for name, tag in self._hg.branchtags().iteritems():
            if ("close" not in self._hg.changelog.read(tag)[5]):
                self._repo.branches.append(
                    Object(name=name, object_id=self._hg[tag].hex()))

        self._repo.repo_tags = [
            Object(name=name, object_id=self._hg[tag].hex())
            for name, tag in self._hg.tags().iteritems()]
        session(self._repo).flush()

    def refresh_commit_info(self, oid, seen, lazy=True):
        from allura.model.repo import CommitDoc
        ci_doc = CommitDoc.m.get(_id=oid)
        if ci_doc and lazy: return False
        obj = self._hg[oid]
        # Save commit metadata
        mo = self.re_hg_user.match(obj.user())
        if mo:
            user_name, user_email = mo.groups()
        else:
            user_name = user_email = obj.user()
        user = Object(
            name=h.really_unicode(user_name),
            email=h.really_unicode(user_email),
            date=datetime.utcfromtimestamp(obj.date()[0]))
        fake_tree = self._tree_from_changectx(obj)
        args = dict(
            tree_id=fake_tree.hex(),
            committed=user,
            authored=user,
            message=h.really_unicode(obj.description() or ''),
            child_ids=[],
            parent_ids=[ p.hex() for p in self.real_parents(obj)
                                 if p.hex() != obj.hex() ])
        if ci_doc:
            ci_doc.update(args)
            ci_doc.m.save()
        else:
            ci_doc = CommitDoc(dict(args, _id=oid))
            try:
                ci_doc.m.insert(safe=True)
            except DuplicateKeyError:
                if lazy: return False
        self.refresh_tree_info(fake_tree, seen, lazy)
        return True

    def refresh_tree_info(self, tree, seen, lazy=True):
        from allura.model.repo import TreeDoc
        if lazy and tree.hex() in seen: return
        seen.add(tree.hex())
        doc = TreeDoc(dict(
                _id=tree.hex(),
                tree_ids=[],
                blob_ids=[],
                other_ids=[]))
        for name, t in tree.trees.iteritems():
            self.refresh_tree_info(t, seen, lazy)
            doc.tree_ids.append(
                dict(name=h.really_unicode(name), id=t.hex()))
        for name, oid in tree.blobs.iteritems():
            doc.blob_ids.append(
                dict(name=h.really_unicode(name), id=oid))
        doc.m.save(safe=False)
        return doc

    def log(self, object_id, skip, count):
        obj = self._hg[object_id]
        candidates = [ obj ]
        result = []
        seen = set()
        while count and candidates:
            candidates.sort(key=lambda c:sum(c.date()))
            obj = candidates.pop(-1)
            if obj.hex() in seen: continue
            seen.add(obj.hex())
            if skip == 0:
                result.append(obj.hex())
                count -= 1
            else:
                skip -= 1
            candidates += self.real_parents(obj)
        return result, [ p.hex() for p in candidates ]

    def open_blob(self, blob):
        fctx = self._hg[blob.commit._id][h.really_unicode(blob.path()).encode('utf-8')[1:]]
        return StringIO(fctx.data())

    def blob_size(self, blob):
        fctx = self._hg[blob.commit._id][h.really_unicode(blob.path()).encode('utf-8')[1:]]
        return fctx.size()

    def _setup_hooks(self, source_path=None):
        'Set up the hg changegroup hook'
        hgrc = os.path.join(self._repo.fs_path, self._repo.name, '.hg', 'hgrc')
        cp = ConfigParser()
        cp.read(hgrc)
        if not cp.has_section('hooks'):
            cp.add_section('hooks')
        url = (tg.config.get('base_url', 'http://localhost:8080')
               + '/auth/refresh_repo' + self._repo.url())
        cp.set('hooks','; = [the next line is required for site integration, do not remove/modify]', '')
        cp.set('hooks','changegroup.sourceforge','curl -s %s' % url)
        with open(hgrc, 'w') as fp:
            cp.write(fp)
        os.chmod(hgrc, 0755)

    def _tree_from_changectx(self, changectx):
        '''Build a fake git-like tree from a changectx and its manifest'''
        root = GitLikeTree()
        for filepath in changectx.manifest():
            fctx = changectx[filepath]
            oid = b2a_hex(fctx.filenode())
            root.set_blob(filepath, oid)
        return root

    def symbolics_for_commit(self, commit):
        branch_heads, tags = super(self.__class__, self).symbolics_for_commit(commit)
        try:
            ctx = self._hg[commit._id]
        except RepoLookupError as e:
            return [], tags
        return [ctx.branch()], tags

    def compute_tree_new(self, commit, tree_path='/'):
        ctx = self._hg[commit._id]
        fake_tree = self._tree_from_changectx(ctx)
        fake_tree = fake_tree.get_tree(tree_path)
        tree = self.refresh_tree_info(fake_tree, set())
        return tree._id

    def commits(self, path=None, rev=None, skip=None, limit=None):
        start = 0
        stop = None
        if skip is not None:
            start = skip
        if limit is not None:
            stop = start + limit
        if path:
            opts = {'pats': [path], 'default': 'path'}
        else:
            opts = {}
        try:
            m = cmdutil.match(self._hg, **opts)
        except Exception as e:
            log.exception('Error walking Hg commits: %s' % e)
            return
        opts = {'rev': ['%s:0' % rev] if rev is not None else rev}
        try:
            revs_iter = cmdutil.walkchangerevs(self._hg, m, opts, lambda *a: None)
        except Exception as e:
            log.exception('Error walking Hg commits: %s' % e)
            return
        for ctx in islice(revs_iter, start, stop):
            yield ctx.hex()

    def commits_count(self, path=None, rev=None):
        return sum(1 for _ in self.commits(path=path, rev=rev))

    def tarball(self, commit):
        if not os.path.exists(self._repo.tarball_path):
            os.makedirs(self._repo.tarball_path)
        archive_name = self._repo.tarball_filename(commit)
        path = os.path.join(self._repo.tarball_path, archive_name)
        filename = os.path.join(self._repo.tarball_path, '%s%s' % (archive_name, '.zip'))
        tmpfilename = os.path.join(self._repo.tarball_path, '%s%s' % (archive_name, '.tmp'))
        if os.path.exists(path):
            rmtree(path)
        try:
            commands.archive(HgUI(), self._hg, path, rev=commit, prefix='')
            basedir = os.path.basename(path)
            zipdir(path, tmpfilename, exclude=basedir + '/.hg_archival.txt')
            os.rename(tmpfilename, filename)
        finally:
            rmtree(path)
            if os.path.exists(tmpfilename):
                os.remove(tmpfilename)

    def is_empty(self):
        return not self._hg or self._hg.heads() == ['\x00'*20]

Mapper.compile_all()
