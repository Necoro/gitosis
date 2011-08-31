# -*- coding: utf-8 -*-
"""
    gitosis.repository
    ~~~~~~~~~~~~~~~~~~

    This module implements functions for dealing with ``git`` repositories.

    :license: GPL
"""

import os
import re
import subprocess
import sys

from gitosis import util
from gitosis.exceptions import GitosisError, GitError


def init(path, git=None, mode=0750, **kwargs):
    """Create a git repository at `path` if missing.

    .. note::

       Leading directories of `path` must exist. Any extra keyword
       arguments are passed to ``git init`` command, for example::

           >>> init("/tmp/foo", template="/tmp/foo-template")

       would result in the following call::

           $ git --git-dir=. init --template=/tmp/foo-template

    :param str path: path to repository to create.
    :param int mode: access permission to set for the newly created repository.
    """
    git = git or "git"

    # a) ensure repository directory is there.
    util.mkdir(path, mode)

    # b) call ``git init`` with any extra keyword arguments given
    args = [git, "--git-dir=.", "init"]
    for item in kwargs.iteritems():
        args.append("--{0}={1}".format(*item))

    code = subprocess.call(args=args, cwd=path,
                           stdout=sys.stderr, close_fds=True)

    if code:  # Make sure it worked.
        raise GitError("init", "exit status {0}".format(code))


def fast_import(
    git_dir,
    commit_msg,
    committer,
    files,
    parent=None,
    ):
    """
    Create an initial commit.
    """
    child = subprocess.Popen(
        args=[
            'git',
            '--git-dir=.',
            'fast-import',
            '--quiet',
            '--date-format=now',
            ],
        cwd=git_dir,
        stdin=subprocess.PIPE,
        close_fds=True,
        )
    files = list(files)
    for index, (path, content) in enumerate(files):
        child.stdin.write("""\
blob
mark :%(mark)d
data %(len)d
%(content)s
""" % dict(
            mark=index+1,
            len=len(content),
            content=content,
            ))
    child.stdin.write("""\
commit refs/heads/master
committer %(committer)s now
data %(commit_msg_len)d
%(commit_msg)s
""" % dict(
            committer=committer,
            commit_msg_len=len(commit_msg),
            commit_msg=commit_msg,
            ))
    if parent is not None:
        assert not parent.startswith(':')
        child.stdin.write("""\
from %(parent)s
""" % dict(
                parent=parent,
                ))
    for index, (path, content) in enumerate(files):
        child.stdin.write('M 100644 :%d %s\n' % (index+1, path))
    child.stdin.close()
    returncode = child.wait()
    if returncode != 0: #pragma: no cover
        raise GitError("fast-import", 'exit status %d' % returncode)


def export(git_dir, path):
    """Export a Git repository to a given path."""
    util.mkdir(path)
    returncode = subprocess.call(
        args=[
            'git',
            '--git-dir=%s' % git_dir,
            'read-tree',
            'HEAD',
            ],
        close_fds=True,
        )
    if returncode != 0: #pragma: no cover
        raise GitError("read-tree", 'exit status %d' % returncode)
    # jumping through hoops to be compatible with git versions
    # that don't have --work-tree=
    env = {}
    env.update(os.environ)
    env['GIT_WORK_TREE'] = '.'
    returncode = subprocess.call(
        args=[
            'git',
            '--git-dir=%s' % os.path.abspath(git_dir),
            'checkout-index',
            '-a',
            '-f',
            ],
        cwd=path,
        close_fds=True,
        env=env,
        )
    if returncode != 0: #pragma: no cover
        raise GitError("checkout-index", 'exit status %d' % returncode)


def has_initial_commit(git_dir):
    """Check if a Git repo contains at least one commit linked by HEAD."""
    child = subprocess.Popen(
        args=[
            'git',
            '--git-dir=.',
            'rev-parse',
            'HEAD',
            ],
        cwd=git_dir,
        stdout=subprocess.PIPE,
        close_fds=True,
        )
    got = child.stdout.read()
    returncode = child.wait()
    if returncode != 0:
        raise GitError("rev-parse", 'exit status %d' % returncode)
    if got == 'HEAD\n':
        return False
    elif re.match('^[0-9a-f]{40}\n$', got):
        return True
    else: #pragma: no cover
        raise GitosisError('Unknown git HEAD: %r' % got)
