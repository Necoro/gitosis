"""
Some utility functions for Gitosis
"""
import errno
import os
import shutil

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
    home = os.path.expanduser("~")
    return os.path.join(home,
        config.get("gitosis", "repositories", default="repositories"))


def getGeneratedFilesDir(config):
    """
        Find the location for the generated Gitosis files.

        Tries:
        - ``gitosis.generate-files-in`` configuration key
        - ``~/gitosis``
    """
    return config.get("gitosis", "generate-files-in",
                      default=os.path.expanduser("~/gitosis"))


def getSSHAuthorizedKeysPath(config):
    return config.get("gitosis", "ssh-authorized-keys-path",
                      default=os.path.expanduser("~/.ssh/authorized_keys"))
