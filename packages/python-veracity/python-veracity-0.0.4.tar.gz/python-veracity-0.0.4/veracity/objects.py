#!/usr/bin/env python

"""
Classes representing all the "objects" used in Veracity.
"""

import os
import time
import shutil
import logging
from collections import defaultdict, OrderedDict

from veracity import vv
from veracity import vscript
from veracity.vv import VeracityException
from veracity import settings


class _Base(object):  # pylint: disable=R0903
    """Shared base class."""

    def _repr(self, *args, **kwargs):
        """Return representation string from the provided arguments.
        @param args: list of arguments to __init__
        @param kwargs: dictionary of keyword arguments to __init__
        @return: __repr__ string
        """
        # Remove unnecessary empty keywords arguments
        for key, value in kwargs.items():
            if value is None:
                del kwargs[key]
        # Return the __repr__ string
        args_repr = ', '.join(repr(arg) for arg in args)
        kwargs_repr = ', '.join(k + '=' + repr(v) for k, v in kwargs.items())
        if args_repr and kwargs_repr:
            kwargs_repr = ', ' + kwargs_repr
        return "{}({}{})".format(self.__class__.__name__, args_repr, kwargs_repr)


class _BaseRepositoryObject(_Base):  # pylint: disable=R0903
    """Shared base class for objects that need a reference to the Repository."""

    def __init__(self, create=True, repo=None, **_kwargs):
        if repo:
            if isinstance(repo, Repository):
                self.repo = repo
            else:
                self.repo = Repository(repo, create=create)
        else:
            logging.warning("'repo' argument missing")
            self.repo = None

    def __eq__(self, other):
        return self.repo == other.repo

    def __ne__(self, other):  # pragma: no cover - not called internally
        return not self == other


class _BaseRepositorySpecObject(_BaseRepositoryObject):
    """Shared base class for objects that also need to store rev/tag/branch."""

    def __init__(self, **kwargs):
        super(_BaseRepositorySpecObject, self).__init__(**kwargs)
        self.rev, self.tag, self.branch = identify(**kwargs)

    @property
    def revid(self):
        """Return the rev/tag/branch value.
        """
        return self.rev or self.tag or self.branch

    @property
    def revspec(self):
        """Return the rev/tag/branch keyword dictionary.
        """
        return keywords(rev=self.rev, tag=self.tag, branch=self.branch)


class _BaseWorkingCopyObject(_Base):  # pylint: disable=R0903
    """Shared base class for objects that need a reference to the WorkingCopy."""

    def __init__(self, work=None, **_kwargs):
        if work:
            if isinstance(work, WorkingCopy):
                self.work = work
            else:
                self.work = WorkingCopy(work)
        else:
            logging.warning("'work' argument missing")
            self.work = None

    def __eq__(self, other):
        return self.work == other.work

    def __ne__(self, other):  # pragma: no cover - not called internally
        return not self == other


def auto_pull(func):
    """Decorator for methods that should call self.pull() before execution.
    """
    def wrapped(self, *args, **kwargs):
        """Wrapped method to call self.pull() before execution.
        """
        if self._auto_pull:  # pylint: disable=W0212
            self.pull(_auto=True)
        return func(self, *args, **kwargs)

    return wrapped


def auto_push(func):
    """Decorator for methods that should call self.push() after execution.
    """
    def wrapped(self, *args, **kwargs):
        """Wrapped method to call self.push() after execution.
        """
        result = func(self, *args, **kwargs)
        if self._auto_push:  # pylint: disable=W0212
            self.push(_auto=True)
        return result

    return wrapped


class Repository(_Base):
    """Represents a Veracity repository."""

    def __init__(self, name, remote=None, create=False, autosync=True):
        """Create/clone an existing repo or reference an existing.
        @param name: name of repository (exiting or new)
        @param remote: local or remote repository to clone
        @param create: allow non-existing repositories to be created
        """
        self.name = name
        self.remote = remote
        self._auto_pull = settings.AUTO_PULL and autosync
        self._auto_push = settings.AUTO_PUSH and autosync
        self._pull_time = 0
        self._push_time = 0
        # Create a new repo if required
        logging.debug("checking for existing repo...")
        if self.name not in vv.parse(vv.run('repos')):
            if self.remote:
                logging.info("cloning '{s}' to '{d}'...".format(s=self.remote, d=self.name))
                vv.run('clone', self.remote, self.name)
            elif create:
                logging.info("creating repo '{n}'...".format(n=self.name))
                vv.run('repo', 'new', self.name)
            else:
                raise VeracityException("repository does not exist: {0}".format(name))

    def __repr__(self):
        return self._repr(self.name)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, basestring):
            return str(self) == other
        elif not isinstance(other, Repository):
            return False
        else:
            return all((isinstance(other, Repository),
                        self.name == other.name))

    def __ne__(self, other):
        return not self == other

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, exc_value, _traceback):
        if exc_value:  # pragma: no cover - cannot be tested with unittest
            logging.error("an exception occurred: {0}".format(exc_value))
        self.delete()  # delete the repository upon exiting the 'with' block

    def __getattr__(self, name):
        if name == 'name':
            raise VeracityException("repository has been deleted")
        else:
            raise AttributeError

    def clone(self):  # pragma: no cover
        raise NotImplementedError

    def incoming(self):  # pragma: no cover
        raise NotImplementedError

    def outgoing(self):  # pragma: no cover
        raise NotImplementedError

    def pull(self, remote=None, _auto=False):
        """Pull from a remote repository.
        @param remote: repository name or URL
        """
        if _auto and time.time() < self._pull_time + settings.MIN_DELAY:
            logging.debug("skipped automatic pull")
            return
        remote = remote or self.remote
        if remote:
            logging.log(logging.DEBUG if _auto else logging.INFO,
                        "pulling from '{s}' to '{d}'...".format(s=remote, d=self))
            vv.run('pull', remote, dest=self.name)
            self._pull_time = time.time()
        else:
            try:
                logging.log(logging.DEBUG if _auto else logging.INFO,
                            "pulling from default to '{d}'...".format(d=self))
                vv.run('pull', dest=self.name)
            except VeracityException:
                logging.warning("no remote repository for pull")
            else:
                self._pull_time = time.time()

    def push(self, remote=None, _auto=False):
        """Push to a remote repository.
        @param remote: repository name or URL
        """
        if _auto and time.time() < self._push_time + settings.MIN_DELAY:
            logging.debug("skipped automatic push")
            return
        remote = remote or self.remote
        if remote:
            logging.log(logging.DEBUG if _auto else logging.INFO,
                        "pushing from '{s}' to '{d}'...".format(s=self, d=remote))
            vv.run('push', remote, src=self.name)
            self._push_time = time.time()
        else:
            try:
                logging.log(logging.DEBUG if _auto else logging.INFO,
                            "pushing from '{s}' to default...".format(s=self))
                vv.run('push', src=self.name)
            except VeracityException:
                logging.warning("no remote repository for push")
            else:
                self._push_time = time.time()

    def sync(self):
        """If enabled, perform an automatic pull and push.
        """
        if self._auto_pull:
            self._pull_time = 0
            self.pull(_auto=True)
        if self._auto_push:
            self._push_time = 0
            self.push(_auto=True)

    @property
    @auto_pull
    def branches(self):
        """Return a list of branches in the repository.
        @return: list of Branches
        """
        branches = []
        logging.debug("getting branches in repo '{n}'...".format(n=self.name))
        for name in vv.parse(vv.run('branches', repo=self.name)):
            branches.append(Branch(name, repo=self, identity=False))
        for branch in branches:
            logging.debug("branch: {0}".format(branch))
        return branches

    @property
    @auto_pull
    def history(self):
        """Return a list of changesets in the repository.
        @return: list of Changesets
        """
        changesets = []
        logging.debug("getting history in repo '{n}'...".format(n=self.name))
        for dictionary in vv.parse(vv.run('history', repo=self.name), 'changesets'):
            changesets.append(Changeset(dictionary, repo=self))
        for changeset in changesets:
            logging.debug("changeset: {0}".format(changeset))
        return changesets

    @auto_pull
    def get_heads(self, branch=None):
        """Return a list of head changesets in the repository.
        @param branch: filter to the specified branch name
        @return: list of Changesets
        """
        changesets = []
        if branch and branch not in self.branches:
            return changesets
        logging.debug("getting heads of '{b}' in repo '{n}'...".format(b=branch or "<all branches>", n=self.name))
        for dictionary in vv.parse(vv.run('heads', repo=self.name, **keywords(branch=branch)), 'changesets'):
            changeset = Changeset(dictionary, repo=self)
            if not branch or branch in changeset.branches:
                changesets.append(changeset)
        for changeset in changesets:
            logging.debug("changeset: {0}".format(changeset))
        return changesets
    heads = property(get_heads)

    @property
    @auto_pull
    def leaves(self):  # pragma: no cover
        raise NotImplementedError

    @property
    @auto_pull
    def tags(self):
        """Return a list of tags in the repository.
        @return: list of Tags
        """
        tags = []
        logging.debug("getting tags in repo '{n}'...".format(n=self.name))
        for label, _local, rev in vv.parse(vv.run('tags', repo=self.name), 'tags'):
            tags.append(Tag(label, repo=self, rev=rev))
        for tag in tags:
            logging.debug("tag: {0}".format(tag))
        return tags

    @property
    @auto_pull
    def stamps(self):
        """Return a list of stamps in the repository.
        @return: list of Stamps
        """
        stamps = []
        logging.debug("getting stamps in repo '{n}'...".format(n=self.name))
        for label, _count in vv.parse(vv.run('stamps', repo=self.name), 'stamps'):
            stamps.append(Stamp(label, repo=self, identity=False))
        for stamp in stamps:
            logging.debug("stamp: {0}".format(stamp))
        return stamps

    @property
    @auto_pull
    def users(self):
        """Return a list of users in the repository.
        @return: list of Users
        """
        users = []
        logging.debug("getting users in repo '{n}'...".format(n=self.name))
        for name in vv.parse(vv.run('users', repo=self.name), 'indented'):
            users.append(User(name, repo=self))
        for user in users:
            logging.debug("user: {0}".format(user))
        return users

    @property
    @auto_pull
    def locks(self):  # pragma: no cover
        """Return a list of locked files in the repository.
        @return: list of Items
        """
        raise NotImplementedError

    def get_user(self):
        """Return the current user for this repository.
        @return: current User or None
        """
        logging.debug("getting the current user in repo '{n}'...".format(n=self.name))
        try:
            return User(vv.run('whoami', repo=self.name), repo=self)
        except VeracityException:  # pragma: no cover - user cannot be "unset"
            return None
    user = property(get_user, doc='')

    @user.setter
    def user(self, name):
        """Set the current user for this repository.
        @param name: name of user
        """
        user = User(name, repo=self)
        logging.info("setting '{u}' as the current user in repo '{r}'...".format(u=user, r=user.repo))
        vv.run('whoami', user, repo=user.repo)
        return user

    @auto_pull
    @auto_push
    def add_branch(self, name, **kwargs):
        """Add a branch head to the repository.
        @param name: name of branch
        @param kwargs: rev, tag, or branch
        @return: new Branch
        """
        branch = Branch(name, repo=self, **kwargs)
        logging.info("adding head of '{b}' at '{i}' in '{r}'...".format(b=branch, i=branch.revid, r=branch.repo))
        vv.run('branch', 'add-head', branch, repo=branch.repo, **branch.revspec)
        return branch

    @auto_pull
    @auto_push
    def add_user(self, name):
        """Add a new user to the repository.
        @param name: name of new user
        @return: new User
        """
        user = User(name, repo=self)
        logging.info("adding user '{u}' to '{r}'...".format(u=user, r=user.repo))
        if user in self.users:
            logging.warning("user '{u}' already exists in '{r}'".format(u=user, r=user.repo))
        else:
            vv.run('user', 'create', user, repo=user.repo)
        return user

    @auto_pull
    @auto_push
    def add_tag(self, label, **kwargs):
        """Add a tag to the repository.
        @param tag: label of new tag
        @param kwargs: rev, tag, or branch
        @return: new Tag
        """
        tag = Tag(label, repo=self, **kwargs)
        logging.info("tagging '{i}' of '{r}' as '{t}'...".format(t=tag, i=tag.revid, r=tag.repo))
        if tag in self.tags:
            logging.warning("tag '{t}' already exists in '{r}'".format(t=tag, r=tag.repo))
        else:
            vv.run('tag', 'add', tag, repo=tag.repo, **tag.revspec)
        return tag

    @auto_pull
    @auto_push
    def add_stamp(self, label, **kwargs):
        """Add a stamp to the repository.
        @param tag: label of new stamp
        @param kwargs: rev, tag, or branch
        @return: new Stamp
        """
        stamp = Stamp(label, repo=self, **kwargs)
        logging.debug("stamping '{i}' in '{r}' as '{s}'...".format(s=stamp, i=stamp.revid, r=stamp.repo))
        vv.run('stamp', 'add', stamp, repo=stamp.repo, **stamp.revspec)
        return stamp

    @auto_pull
    @auto_push
    def move_branch(self, name, **kwargs):
        """Move a branch head in the repository.
        @param name: name of branch
        @param kwargs: rev, tag, or branch
        @return: moved Branch
        """
        branch = Branch(name, repo=self, **kwargs)
        logging.info("moving head of '{b}' to '{i}' in '{r}'...".format(b=branch, i=branch.revid, r=branch.repo))
        vv.run('branch', 'move-head', branch, repo=branch.repo, **branch.revspec)
        return branch

    @auto_pull
    @auto_push
    def move_tag(self, label, **kwargs):
        """Move a tag in the repository.
        @param tag: label of tag to move
        @param kwargs: rev, tag, or branch
        @return: moved Tag
        """
        tag = Tag(label, repo=self, **kwargs)
        logging.info("moving tag '{t}' to '{i}' in '{r}'...".format(t=tag, i=tag.revid, r=tag.repo))
        vv.run('tag', 'move', tag, repo=tag.repo, **tag.revspec)
        return tag

    @auto_pull
    @auto_push
    def rename_user(self, old, new):
        """Rename a user in the repository.
        @param old: old username
        @param new: new username
        """
        user = User(new, repo=self)
        logging.info("renaming user '{u1}' to '{u2}' in '{r}'...".format(u1=old, u2=user, r=user.repo))
        vv.run('user', 'rename', old, user, repo=user.repo)
        return user

    @auto_push
    def close_branch(self, name):
        """Close a branch in the repository.
        @param name: name of branch to close
        @return: closed Branch
        """
        branch = Branch(name, repo=self, identity=False)
        logging.info("closing branch '{b}' in '{r}'...".format(b=branch, r=branch.repo))
        if branch not in self.branches:
            logging.warning("branch '{b}' is not open in '{r}'".format(b=branch, r=branch.repo))
        else:
            vv.run('branch', 'close', branch.name, repo=branch.repo)
        return branch

    @auto_push
    def reopen_branch(self, name):
        """Reopen a branch in the repository.
        @param name: name of branch to reopen
        @return: opened Branch
        """
        branch = Branch(name, repo=self, identity=False)
        logging.info("reopening branch '{b}' in '{r}'...".format(b=branch, r=branch.repo))
        if branch in self.branches:
            logging.warning("branch '{b}' is already open in '{r}'".format(b=branch, r=branch.repo))
        else:
            vv.run('branch', 'reopen', branch, repo=branch.repo)
        return branch

    @auto_push
    def deactivate_user(self, name):
        """Deactivate a user in the repository.
        @param name: name of user to deactivate
        @return: deactivated User
        """
        user = User(name, repo=self)
        logging.info("deactivating user '{u}' in '{r}'...".format(u=user, r=user.repo))
        vv.run('user', 'set-inactive', user, repo=user.repo)
        return user

    @auto_push
    def activate_user(self, name):
        """Activate a user in the repository.
        @param name: name of user to activate
        @return: activated User
        """
        user = User(name, repo=self)
        logging.info("activating user '{u}' in '{r}'...".format(u=user, r=user.repo))
        vv.run('user', 'set-active', user, repo=user.repo)
        return user

    @auto_pull
    @auto_push
    def remove_branch(self, label, **kwargs):
        """Remove a branch head from the repository.
        @param name: name of branch head to remove
        @param kwargs: rev, tag, or branch
        """
        branch = Branch(label, repo=self, **kwargs)
        logging.info("removing head of '{b}' from '{i}' in '{r}'...".format(b=branch, i=branch.revid, r=branch.repo))
        vv.run('branch', 'remove-head', branch, repo=branch.repo, **branch.revspec)

    @auto_pull
    @auto_push
    def remove_tag(self, label):
        """Remove a tag from the repository.
        @param tag: label of tag to remove
        """
        tag = Tag(label, repo=self, identity=False)
        logging.info("removing tag '{t}' in '{r}'...".format(t=tag, r=tag.repo))
        if tag not in self.tags:
            logging.warning("tag '{t}' does not exist in '{r}'".format(t=tag, r=tag.repo))
        else:
            vv.run('tag', 'remove', tag, repo=tag.repo)

    @auto_pull
    @auto_push
    def remove_stamp(self, label, **kwargs):
        """Remove a stamp from the repository.
        @param tag: label of stamp to remove
        @param kwargs: rev, tag, or branch
        """
        stamp = Stamp(label, repo=self, **kwargs)
        logging.info("removing stamp '{s}' from '{i}' in '{r}'...".format(s=stamp, i=stamp.revid, r=stamp.repo))
        vv.run('stamp', 'remove', stamp, repo=stamp.repo, **stamp.revspec)

    @auto_pull
    def checkout(self, path, **kwargs):
        """Check out a new working copy to the specified path.
        @param path: path for the new working copy
        @param kwargs: rev, tag, or branch
        @return: new WorkingCopy
        """
        rev, tag, branch = identify(default=True, **kwargs)
        path = os.path.expanduser(path)
        logging.info("checking out '{i}' of '{r}' to '{p}'...".format(p=path, i=(rev or tag or branch), r=self))
        if not os.path.exists(path):
            os.makedirs(path)
        os.chdir(path)
        vv.run('checkout', self, **keywords(rev=rev, tag=tag, branch=branch))
        return WorkingCopy(path, repo=self)

    @auto_pull
    def export(self, path, **kwargs):  # pragma: no cover
        raise NotImplementedError

    @auto_pull
    def zip(self, path, **kwargs):  # pragma: no cover
        raise NotImplementedError

    @auto_push
    def request_build(self, name, series, environment, status, cid, branch=None):
        """Request a build of the repository.
        @param name: name for the build
        @param series: alias of a build series
        @param environment: alias of an environment
        @param status: alias of the initial build state
        @param cid: changeset identifier (unique revision)
        @param branch: optional branch name to associate with the build
        @return new BuildRequest
        """
        logging.info("requesting [{s}] build of '{c}' for [{e}] in '{r}'...".format(s=series, e=environment,
                                                                                    c=cid, r=self))
        args = [name, series, environment, status, cid] + ([branch] if branch else [])
        bid, cid = next(vscript.parse(vscript.report_build(self, 'new', *args), style='builds'))
        return BuildRequest(bid, cid, name=name, series=series, environment=environment,
                            status=status, branch=branch, repo=self)

    @auto_pull
    def get_build(self, environment, status, order=None):
        """Get the next pending build request in the repository.
        @param environment: alias for the current environment
        @param status: alias for the initial build state
        @param order: return the 'OLDEST' or 'NEWEST' request
        @return: pending BuildRequest
        """
        logging.debug("getting the next build request for [{e}] in '{r}'...".format(e=environment, r=self))
        args = [environment, order or BuildRequest.OLDEST, status]
        try:
            bid, cid = next(vscript.parse(vscript.report_build(self, 'get-pending-build', *args), style='builds'))
        except StopIteration:
            return None
        else:
            return BuildRequest(bid, cid, environment=environment, status=status, repo=self)

    @auto_push
    def update_build(self, bid, status):
        """Update the build request state in the repository.
        @param bid: build request identifier
        @param status: alias for a build state
        """
        logging.info("updating build '{b}' to status '{s}' in '{r}'...".format(b=bid, s=status, r=self))
        vscript.report_build(self, 'update', bid, status)

    @auto_push
    def delete_build(self, bid):
        """Delete the build request in the repository.
        @param bid: build request identifier
        """
        logging.info("deleting build '{b}' in '{r}'...".format(b=bid, r=self))
        vscript.report_build(self, 'delete', bid)

    @property
    @auto_pull
    def builds(self):
        """Get a list of active build requests in the repository.
        @return: iterator of BuildRequests
        """
        logging.debug("getting all build requests in '{r}'...".format(r=self))
        for bid, cid in vscript.parse(vscript.report_build(self, 'list'), style='builds'):
            if bid and cid:
                request = BuildRequest(bid, cid, repo=self)
                logging.debug("build request: {0}".format(request))
                yield request

    @builds.deleter
    @auto_pull
    @auto_push
    def builds(self):
        """Delete all build requests in the repository.
        """
        logging.info("deleting all build requests in '{r}'...".format(r=self))
        for request in self.builds:
            request.delete()

    def delete(self):
        """Delete the repository.
        """
        logging.info("deleting repo '{n}'...".format(n=self.name))
        if self.name not in vv.repos():
            logging.warning("repository has already been deleted: {0}".format(self))
        else:
            vv.run('repo', 'delete', self.name)
        del self.name  # force VeracityException on next access attempt


def in_path(func):
    """Decorator for methods that must be run inside self.path.
    """
    def wrapped(self, *args, **kwargs):
        """Wrapped method to enter self.path before execution.
        """
        try:
            logging.debug("entering path {0}...".format(self.path))
            os.chdir(self.path)
        except (VeracityException, OSError) as exception:
            logging.warning(exception)
        return func(self, *args, **kwargs)
    return wrapped


def out_path(func):
    """Decorator for methods that must be run outside self.path.
    """
    def wrapped(self, *args, **kwargs):
        """Wrapped method to exit self.path before execution.
        """
        parent = os.path.dirname(self.path)
        logging.debug("exiting to parent {0}...".format(parent))
        os.chdir(parent)
        return func(self, *args, **kwargs)
    return wrapped


class WorkingCopy(_BaseRepositoryObject):
    """Represents a working copy created from a changeset."""

    def __init__(self, path, **kwargs):
        """Create or reference an existing working copy.
        @param path: path to working copy
        @param kwargs: repo and rev/tag/branch
        """
        super(WorkingCopy, self).__init__(**kwargs)
        self.path = path
        # Get the repository from the path if it was not specified
        if not self.repo:
            try:
                os.chdir(path)
            except OSError:  # path does not exist and no repo specified
                raise VeracityException("invalid path: {0}".format(path))
            else:  # path exists; get the repo from the working copy
                self.repo = Repository(vv.run('repo'))
        # Make the path a working copy if not already so
        try:
            os.chdir(self.path)
        except OSError:  # path does not exist; check out a new working copy
            self.repo.checkout(self.path)
        else:  # path exists; determine if it's already a working copy
            if not self.valid():  # not a working copy; check out a new one
                self.repo.checkout(self.path)

    def __repr__(self):
        return self._repr(self.path, branch=self.branch, repo=self.repo)

    def __str__(self):
        return self.path

    def __eq__(self, other):
        if not isinstance(other, WorkingCopy):
            return False
        else:
            return all((super(WorkingCopy, self).__eq__(other),
                        self.path == other.path))

    def __ne__(self, other):
        return not self == other

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, exc_value, _traceback):
        if exc_value:  # pragma: no cover - cannot be tested with unittest
            logging.error("an exception occurred: {0}".format(exc_value))
        self.delete()  # delete the working copy upon exiting the 'with' block

    def __getattr__(self, name):
        if name == 'path':
            raise VeracityException("working copy has been deleted")
        else:
            raise AttributeError

    @property
    @in_path
    def branch(self):
        """Get the currently attached branch.
        @return: current Branch
        """
        name = vv.run('branch')
        if name:
            return Branch(name, repo=self.repo, identity=False)
        else:
            return None

    @branch.setter
    def branch(self, name):
        """Alias for attaching the working copy to a branch.
        @return: newly attached Branch
        """
        return self.attach(name)

    @in_path
    def attach(self, name):
        """Attach the working copy to a branch.
        @param name: branch name
        @return: new Branch
        """
        if name:
            logging.info("attaching {p} to branch '{n}'...".format(p=self.path, n=name))
            try:
                vv.run('branch', 'attach', name)
            except VeracityException:
                logging.debug("branch could not be attached, creating a new branch...")
                vv.run('branch', 'new', name)
        else:  # detach from current
            self.detach(self.branch.name)
        return Branch(name, repo=self.repo, identity=False)

    @in_path
    def detach(self, name):
        """Detach the working copy from a branch.
        @param name: branch name
        """
        if name:
            logging.info("detaching {p} from branch '{n}'...".format(p=self.path, n=name))
            vv.run('branch', 'detach', name)

    @in_path
    def update(self, **kwargs):
        """Update the working copy to the specified changeset.
        """
        rev, tag, branch = identify(**kwargs)
        logging.info("updating {w} to '{i}'...".format(w=self, i=(rev or tag or branch)))
        vv.run('update', detached=True, **keywords(rev=rev, tag=tag, branch=branch))
        if branch:
            self.attach(branch)
        return self.parent

    @in_path
    def add(self, path):  # pragma: no cover
        """Add an item to track.
        @param path: path to a file or directory
        @return: newly tracked Item
        """
        raise NotImplementedError

    @in_path
    def remove(self, path):  # pragma: no cover
        """Remove an item to no longer track.
        @param path: path to a file or directory
        """
        raise NotImplementedError

    @in_path
    def rename(self, old, new):  # pragma: no cover
        """Rename a tracked item.
        @param path: path to a file or directory
        @return: renamed Item
        """
        raise NotImplementedError

    def get_parent(self):
        """Alias for getting the first parent changeset.
        @return: parent Changeset
        """
        return self.parents[0]
    parent = property(get_parent, doc='')

    @property
    @in_path
    def parents(self):
        """Return a list of parent changesets.
        @return: list of parent Changesets
        """
        changesets = []
        logging.debug("getting parent changesets...")
        for dictionary in vv.parse(vv.run('parents'), 'changesets'):
            changesets.append(Changeset(dictionary, repo=self.repo))
        for changeset in changesets:
            logging.debug("changeset: {0}".format(changeset))
        return changesets

    @in_path
    def status(self):
        """Return a list of Items. An empty list indicates no changes.
        @return: list of Items
        """
        items = OrderedDict()
        logging.debug("getting status items...")
        for change, path in vv.parse(vv.run('status'), 'files'):
            if path in items:
                items[path].changes.add(change)
            else:
                items[path] = Item(path, changes=[change], work=self)
        for item in items.itervalues():
            logging.debug("item: {0}".format(item))
        return items.values()

    @in_path
    def commit(self, message):  # pragma: no cover
        """Commit the current working copy changes.
        @param message: commit message
        @return: new Changeset
        """
        raise NotImplementedError

    @in_path
    def merge(self):  # pragma: no cover
        raise NotImplementedError

    @in_path
    def resolve(self):  # pragma: no cover
        raise NotImplementedError

    @in_path
    def revert(self, path=None, backups=False):
        """Revert the current working copy changes.
        @param path: working copy path
        @param backups: indicates backup files should be created
        """
        logging.info("reverting changes in {p}...".format(p=self.path))
        if path:
            vv.run('revert', path, no_backups=(not backups))
        else:
            vv.run('revert', all=True, no_backups=(not backups))

    @in_path
    def valid(self):
        """Determine if this is a valid working copy.
        @return: indicates working copy is valid
        """
        logging.debug("determining if working copy is valid...")
        try:
            return self.repo.name == vv.run('repo')
        except VeracityException:
            logging.debug("working copy is invalid")
            return False

    def chdir(self, rel='.'):
        """Change the current directory relative to the working copy.
        @param rel: path relative to the working copy
        """
        path = os.path.normpath(os.path.join(self.path, rel))
        logging.debug("entering working copy directory {0}...".format(path))
        os.chdir(path)

    @out_path
    def delete(self):
        """Delete the working copy.
        """
        logging.info("deleting '{p}'...".format(p=self.path))
        if not os.path.exists(self.path):
            logging.warning("working copy has already been deleted: {0}".format(self))
        else:
            shutil.rmtree(self.path)
        del self.path  # force VeracityException on next access attempt


class Item(_BaseWorkingCopyObject):
    """Represents a file or directory identified by Veracity."""

    ADDED = 'Added'
    ATTRIBUTES = 'Attributes'
    FOUND = 'Found'
    LOST = 'Lost'
    MODIFIED = 'Modified'
    REMOVED = 'Removed'
    RENAMED = 'Renamed'

    def __init__(self, path, changes=None, **kwargs):
        """Represent a working copy item.
        @param path: relative file path
        @param changes: set of changes to the file
        @param kwargs: work
        """
        super(Item, self).__init__(**kwargs)
        self.path = path
        self.changes = set(changes) if changes else set()

    def __repr__(self):
        return self._repr(self.path, changes=self.changes)

    def __str__(self):
        if self.changes:
            return "{p} ({c})".format(p=self.path, c=', '.join(self.changes))
        else:
            return "{p}".format(p=self.path)

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        else:
            return all((super(Item, self).__eq__(other),
                        self.path == other.path))

    def __ne__(self, other):
        return not self == other

    def revert(self):  # pragma: no cover
        raise NotImplementedError

    def move(self):  # pragma: no cover
        raise NotImplementedError

    def rename(self):  # pragma: no cover
        raise NotImplementedError

    def remove(self):  # pragma: no cover
        raise NotImplementedError

    def lock(self):
        """Lock the item.
        """
        logging.info("locking {0}...".format(self.path))
        vv.run('lock', self.path)

    def unlock(self):
        """Unlock the item.
        """
        logging.info("unlocking {0}...".format(self.path))
        vv.run('unlock', self.path)


class Changeset(_BaseRepositoryObject):
    """Represents a changeset in a Veracity repository."""

    def __init__(self, dictionary, **kwargs):
        """Parse the changeset attributes from a dictionary.
        @param dictionary: defaultdict(list) parsed from changeset text
        @param kwargs: repo
        """
        super(Changeset, self).__init__(**kwargs)
        if isinstance(dictionary, dict):
            self.rev = dictionary['revision'][0].split(":")[-1]
            self._branches = dictionary['branch']
            self._tags = dictionary['tag']
        else:
            self.rev = dictionary  # assume single revision string was given
            self._branches = []
            self._tags = []

    def __repr__(self):
        dictionary = defaultdict(list)
        dictionary['revision'] = self.rev
        dictionary['branch'] = self._branches
        dictionary['tag'] = self._tags
        return self._repr(dictionary, repo=self.repo)

    def __str__(self):
        return self.rev[:10]

    def __eq__(self, other):
        if isinstance(other, basestring):
            return self.rev == other
        elif not isinstance(other, Changeset):
            return False
        else:
            return all((super(Changeset, self).__eq__(other),
                        self.repo == other.repo,
                        self.rev == other.rev))

    def __ne__(self, other):
        return not self == other

    def get_branches(self):
        """Return a list of Branches headed at this changeset.
        @return: list of Branches
        """
        return [Branch(name, repo=self.repo, rev=self.rev) for name in self._branches]
    branches = property(get_branches, doc='')

    def get_tags(self):
        """Return a list of Tags at this changeset.
        @return: list of Tags
        """
        return [Tag(label, repo=self.repo, rev=self.rev) for label in self._tags]
    tags = property(get_tags, doc='')

    def checkout(self, path):
        """Check out this changeset.
        @param path: path for the new working copy
        @return: new WorkingCopy
        """
        return self.repo.checkout(path, rev=self.rev)


class Branch(_BaseRepositorySpecObject):
    """Represents a branch in a particular Veracity repository."""

    MASTER = 'master'

    def __init__(self, name, **kwargs):
        """Represent a branch.
        @param name: branch name
        @param kwargs: repo and rev/tag/branch
        """
        super(Branch, self).__init__(**kwargs)
        self.name = name

    def __repr__(self):
        return self._repr(self.name, repo=self.repo)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, basestring):
            return str(self) == other
        elif not isinstance(other, Branch):
            return False
        else:
            return all((super(Branch, self).__eq__(other),
                        self.name == other.name,
                        self.rev == other.rev,
                        self.tag == other.tag,
                        self.branch == other.branch))

    def __ne__(self, other):
        return not self == other

    def move(self, **kwargs):
        """Move a branch head.
        @param kwargs: rev, tag, or branch
        """
        return self.repo.move_branch(self.name, **kwargs)

    def remove(self):
        """Remove the branch head.
        """
        self.repo.remove_branch(self.name, rev=self.rev, tag=self.tag, branch=self.branch)

    def close(self):
        """Close the branch.
        """
        self.repo.close_branch(self.name)

    def reopen(self):
        """Reopen the branch.
        """
        self.repo.reopen_branch(self.name)


class Stamp(_BaseRepositorySpecObject):
    """Represents a stamp applied to changesets."""

    def __init__(self, label, **kwargs):
        """Represent a stamp.
        @param label: stamp label
        @param kwargs: repo and rev/tag/branch
        """
        super(Stamp, self).__init__(**kwargs)
        self.label = label

    def __repr__(self):
        return self._repr(self.label, repo=self.repo, **self.revspec)

    def __str__(self):
        return self.label

    def __eq__(self, other):
        if isinstance(other, basestring):
            return str(self) == other
        elif not isinstance(other, Stamp):
            return False
        else:
            return all((super(Stamp, self).__eq__(other),
                        self.label == other.label))

    def __ne__(self, other):
        return not self == other

    def remove(self):
        """Remove the stamp.
        """
        self.repo.remove_stamp(self.label, rev=self.rev, tag=self.tag, branch=self.branch)


class Tag(_BaseRepositorySpecObject):
    """Represents a tag applied to a particular changeset."""

    def __init__(self, label, **kwargs):
        """Represent a tag.
        @param label: tag label
        @param kwargs: repo and rev/tag/branch
        """
        super(Tag, self).__init__(**kwargs)
        self.label = label

    def __repr__(self):
        return self._repr(self.label, repo=self.repo, **self.revspec)

    def __str__(self):
        return self.label

    def __eq__(self, other):
        if isinstance(other, basestring):
            return str(self) == other
        elif not isinstance(other, Tag):
            return False
        else:
            return all((super(Tag, self).__eq__(other),
                        self.label == other.label))

    def __ne__(self, other):
        return not self == other

    def move(self, **kwargs):
        """Move the tag.
        @param kwargs: rev, tag, or branch
        """
        return self.repo.move_tag(self.label, **kwargs)

    def remove(self):
        """Remove the tag.
        """
        self.repo.remove_tag(self.label)


class User(_BaseRepositoryObject):
    """Represents a user in a Veracity repository."""

    NOBODY = 'nobody'

    def __init__(self, name, **kwargs):
        """Represent a user.
        @param name: user name
        @param kwargs: repo
        """
        super(User, self).__init__(**kwargs)
        self.name = name

    def __repr__(self):
        return self._repr(self.name, repo=self.repo)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, basestring):
            return str(self) == other
        elif not isinstance(other, User):
            return False
        else:
            return all((super(User, self).__eq__(other),
                        self.name == other.name))

    def __ne__(self, other):
        return not self == other

    def set(self):
        """Set the user.
        """
        self.repo.user = self.name

    def activate(self):
        """Active the user.
        """
        self.repo.activate_user(self.name)

    def deactivate(self):
        """Deactivate the user.
        """
        self.repo.deactivate_user(self.name)

    def rename(self, name):
        """Rename the user.
        @param name: new username
        """
        return self.repo.rename_user(self.name, name)


class BuildRequest(_BaseRepositoryObject):
    """Represents a build request."""

    OLDEST = 'OLDEST'
    NEWEST = 'NEWEST'

    def __init__(self, bid, cid, name=None, series=None, environment=None,
                 status=None, branch=None, **kwargs):
        """Represent a build request.
        @param bid: build request identifier
        @param cid: changeset identifier (unique revision)
        @param name: name for the build
        @param series: alias of a build series
        @param environment: alias of an environment
        @param status: alias of the initial build state
        @param branch: optional branch name to associate with the build
        @param kwargs: repo
        """
        super(BuildRequest, self).__init__(**kwargs)
        self.bid = bid or '?' * 10
        self.changeset = Changeset(cid, repo=self.repo)
        # TODO: determine which attributes are actually needed by the class
        self.name = name
        self.series = series
        self.environment = environment
        self.status = status
        self.branch = branch

    def __repr__(self):
        return self._repr(self.bid, self.changeset.rev, name=self.name,
                          series=self.series, environment=self.environment,
                          status=self.status, branch=self.branch,
                          repo=self.repo)

    def __str__(self):
        return "'{b}' of '{c}'".format(b=self.bid[:10], c=self.changeset)

    def __eq__(self, other):
        if isinstance(other, basestring):
            return str(self.bid) == other
        elif not isinstance(other, BuildRequest):
            return False
        else:
            return all((super(BuildRequest, self).__eq__(other),
                        self.bid == other.bid))

    def __ne__(self, other):
        return not self == other

    def update(self, status):
        """Update the build state.
        @param status: alias for a build state
        """
        self.repo.update_build(self.bid, status)
        self.status = status

    def delete(self):
        """Delete the build request.
        """
        self.repo.delete_build(self.bid)
        self.status = None


def identify(default=False, identity=True, **kwargs):
    """Return the (rev, branch, tag) identifying a changeset.
    @param default: allow the branch to default to master
    @param identity: indicates arguments must identify a unique changeset
    @param kwargs: rev, tag, or branch
    @return: rev, tag, branch (only one is not None)

    >>> identify(rev=1, tag=None, branch=None)
    (1, None, None)

    >>> identify(rev=None, tag=None, branch=None, default=True)
    (None, None, 'master')

    """
    rev = kwargs['rev'] if 'rev' in kwargs else None
    tag = kwargs['tag'] if 'tag' in kwargs else None
    branch = kwargs['branch'] if 'branch' in kwargs else None
    count = (rev, branch, tag).count(None)
    if count == 3:  # all identifiers are None
        if default:
            branch = Branch.MASTER
            logging.debug("defaulting to branch: {0}".format(branch))
        elif identity:
            raise ValueError("no changeset identifiers")
    elif count == 2:  # one identifier is not None
        pass
    else:  # multiple identifiers are not None
        raise ValueError("multiple changeset identifiers: rev={r}, branch={b}, tag={t}".format(r=rev, b=branch, t=tag))

    return rev, tag, branch


def keywords(**kwargs):
    """Return a keyword dictionary with empty values removed.

    >>> keywords(a=123, b=True, c=False, d=None)
    {'a': 123, 'b': True}

    """
    return {k: v for k, v in kwargs.iteritems() if v}
