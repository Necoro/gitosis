"""
Gitosis functions for dealing with Git repositories.
"""
import os
import re
import subprocess
import sys

from gitosis import util
from gitosis.exceptions import GitosisError, GitError


def init(
    path,
    template=None,
    _git=None,
    mode=0750,
    ):
    """
    Create a git repository at C{path} (if missing).

    Leading directories of C{path} must exist.

    @param path: Path of repository create.

    @type path: str

    @param template: Template directory, to pass to C{git init}.

    @type template: str

    @param mode: Permissions for the new reposistory

    @type mode: int
    """
    if _git is None:
        _git = 'git'

    util.mkdir(path, mode)
    args = [
        _git,
        '--git-dir=.',
        'init',
        ]
    if template is not None:
        args.append('--template=%s' % template)
    returncode = subprocess.call(
        args=args,
        cwd=path,
        stdout=sys.stderr,
        close_fds=True,
        )
    if returncode != 0: #pragma: no cover
        raise GitError("init", 'exit status %d' % returncode)


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
