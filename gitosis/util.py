"""
Some utility functions for Gitosis
"""
import errno
import os
import shutil
from ConfigParser import NoSectionError, NoOptionError

def mkdir(newdir, mode=0777):
    """
        Like os.mkdir, but already existing directories do not raise an error.
    """
    _sysfunc(os.mkdir, [errno.EEXIST], newdir, mode)

def unlink(filename):
    """
        Like os.unlink, but non-existing files do not raise an error.
    """
    _sysfunc(os.unlink, [errno.ENOENT], filename)

def rmtree(directory):
    """
        Like shutil.rmtree, but non-existing trees do not raise an error.
    """
    _sysfunc(shutil.rmtree, [errno.ENOENT], directory)

def _sysfunc(func, ignore, *args, **kwds):
    """
    Run the specified function, ignoring the specified errno if raised, and
    raising other errors.
    """
    # We use * and ** correctly here
    # pylint: disable-msg=W0142
    if not ignore: # pragma: no cover
        ignore = []
    try:
        func(*args, **kwds)
    except OSError, ex:
        if ex.errno in ignore:
            pass
        else:
            raise

def getRepositoryDir(config):
    """
        Find the location of the Git repositories.

        Tries: 
        - ``gitosis.repositories`` configuration key (see note)
        - ``~/repositories``

        Note: If the configuration key is a relative path, it is appended onto
        the homedir for the gitosis user.
    """
    repositories = os.path.expanduser('~')
    try:
        path = config.get('gitosis', 'repositories')
    except (NoSectionError, NoOptionError):
        repositories = os.path.join(repositories, 'repositories')
    else:
        repositories = os.path.join(repositories, path)
    return repositories

def getGeneratedFilesDir(config):
    """
        Find the location for the generated Gitosis files.

        Tries: 
        - ``gitosis.generate-files-in`` configuration key
        - ``~/gitosis``
    """
    try:
        generated = config.get('gitosis', 'generate-files-in')
    except (NoSectionError, NoOptionError):
        generated = os.path.expanduser('~/gitosis')
    return generated

def getSSHAuthorizedKeysPath(config):
    try:
        path = config.get('gitosis', 'ssh-authorized-keys-path')
    except (NoSectionError, NoOptionError):
        path = os.path.expanduser('~/.ssh/authorized_keys')
    return path
