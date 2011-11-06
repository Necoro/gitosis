# -*- coding: utf-8 -*-
"""
    gitosis.exceptions
    ~~~~~~~~~~~~~~~~~~

    This module defines a couple of exceptions raised in different
    parts of :mod:`gitosis`.

    :license: GPL
"""

from __future__ import unicode_literals


class GitosisError(Exception):
    """Base class for all :mod:`gitosis` exceptions."""


class ImproperlyConfigured(GitosisError):
    """Exception raised when something is wrong with :mod:`gitosis`
    configuration. For example when the config file is missing or
    doesn't contain required configuration variable.
    """


class GitError(GitosisError):
    """Exception raised when ``git`` comand failed to execute."""
    def __init__(self, command, *args):
        self.command = command
        super(GitosisError, self).__init__(*args)

    def __str__(self):
        return "git {0} failed: {1}".format(self.command,
                                            ": ".join(self.args))
