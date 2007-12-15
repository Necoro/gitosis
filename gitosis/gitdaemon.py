"""
Gitosis git-daemon functionality.

Handles the ``git-daemon-export-ok`` marker files for all repositories managed
by Gitosis.
"""
import errno
import logging
import os

# C0103 - 'log' is a special name
# pylint: disable-msg=C0103
log = logging.getLogger('gitosis.gitdaemon')

from gitosis import util
from gitosis.configutil import getboolean_default

def export_ok_path(repopath):
    """
    Return the path the ``git-daemon-export-ok`` marker for a given repository.
    """
    path = os.path.join(repopath, 'git-daemon-export-ok')
    return path

def allow_export(repopath):
    """Create the ``git-daemon-export-ok`` marker for a given repository."""
    path = export_ok_path(repopath)
    file(path, 'a').close()

def deny_export(repopath):
    """Remove the ``git-daemon-export-ok`` marker for a given repository."""
    path = export_ok_path(repopath)
    util.unlink(path)

def _extract_reldir(topdir, dirpath):
    """
    Find the relative directory given a base directory & a child directory.
    """
    if topdir == dirpath:
        return '.'
    prefix = topdir + '/'
    assert dirpath.startswith(prefix)
    reldir = dirpath[len(prefix):]
    return reldir

def _is_global_repo_export_ok(config):
    """
    Does the global Gitosis configuration allow daemon exporting?
    """
    global_enable = getboolean_default(config, 'gitosis', 'daemon', False)
    log.debug(
        'Global default is %r',
        {True: 'allow', False: 'deny'}.get(global_enable),
        )
    return global_enable

def _is_repo_export_ok(global_enable, config, reponame):
    """
    Does the Gitosis configuration for the named reposistory allow daemon
    exporting?
    """
    section = 'repo %s' % reponame
    return getboolean_default(config, section, 'daemon', global_enable)

def _set_export_ok_single(enable, name, dirpath, repo):
    """
    Manage the ``git-daemon-export-ok`` marker for a single repository.
    """
    repopath = os.path.join(dirpath, repo)
    if enable:
        log.debug('Allow %r', name)
        allow_export(repopath)
    else:
        log.debug('Deny %r', name)
        deny_export(repopath)

def set_export_ok(config):
    """
    Walk all repositories owned by Gitosis, and manage the
    ``git-daemon-export-ok`` markers.
    """
    repositories = util.getRepositoryDir(config)
    global_enable = _is_global_repo_export_ok(config)

    def _error(ex):
        """Ignore non-existant items."""
        if ex.errno == errno.ENOENT:
            pass
        else:
            raise ex

    for (dirpath, dirnames, _) \
            in os.walk(repositories, onerror=_error):
        # oh how many times i have wished for os.walk to report
        # topdir and reldir separately, instead of dirpath
        reldir = _extract_reldir(
            topdir=repositories,
            dirpath=dirpath,
            )

        log.debug('Walking %r, seeing %r', reldir, dirnames)

        to_recurse = []
        repos = []
        for dirname in dirnames:
            if dirname.endswith('.git'):
                repos.append(dirname)
            else:
                to_recurse.append(dirname)
        dirnames[:] = to_recurse

        for repo in repos:
            name, ext = os.path.splitext(repo)
            if reldir != '.':
                name = os.path.join(reldir, name)
            assert ext == '.git'
            
            enable = _is_repo_export_ok(global_enable, config, name)
            _set_export_ok_single(enable, name, dirpath, repo)
