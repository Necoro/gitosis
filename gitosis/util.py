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
    try:
        os.mkdir(newdir, mode)
    except OSError, ex:
        if ex.errno == errno.EEXIST:
            pass
        else:
            raise

def unlink(filename):
    """
        Like os.unlink, but non-existing files do not raise an error.
    """
    try:
        os.unlink(filename)
    except OSError, ex:
        if ex.errno == errno.ENOENT:
            pass
        else:
            raise

def rmtree(directory):
    """
        Like shutil.rmtree, but non-existing trees do not raise an error.
    """
    try:
        shutil.rmtree(directory)
    except OSError, ex:
        if ex.errno == errno.ENOENT:
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
