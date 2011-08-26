# -*- coding: utf-8 -*-
"""
    gitosis.util
    ~~~~~~~~~~~~

    This module implements a bunch of utility functions for :mod:`gitosis`.

    :license: GPL
"""

import errno
import os
import shutil
import warnings


def catch(func, ignore=[]):
    """Run the specified function, ignoring the specified `errno` if
    raised, and re-raising other errors.
    """
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OSError as e:
            if e.errno not in ignore:
                raise
    return inner


mkdir = catch(os.mkdir, [errno.EEXIST])
unlink = catch(os.unlink, [errno.ENOENT])
rmtree = catch(shutil.rmtree, [errno.ENOENT])


# Deprecated folks.

def getRepositoryDir(config):
    warnings.warn("deprecated", DeprecationWarning)
    return config.repository_dir


def getGeneratedFilesDir(config):
    warnings.warn("deprecated", DeprecationWarning)
    return config.generated_files_dir

def getSSHAuthorizedKeysPath(config):
    warnings.warn("deprecated", DeprecationWarning)
    return config.ssh_authorized_keys_path
