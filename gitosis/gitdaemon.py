# -*- coding: utf-8 -*-
"""
    gitosis.gitdaemon
    ~~~~~~~~~~~~~~~~~

    This module handles the ``git-daemon-export-ok`` marker files for
    all repositories managed by :mod:`gitosis`.

    :license: GPL
"""

import logging
import os

from gitosis import util

log = logging.getLogger("gitosis.gitdaemon")


def export_path(path):
    """Returns ``git-daemon-export-ok`` path for a given repository."""
    return os.path.join(path, "git-daemon-export-ok")


def export_one(path, enable=True):
    """Enables (default) or disables repository export at a given
    `path`, based on `enable` value.
    """
    if enable:
        log.debug("Allow {0!r}".format(path))
        open(export_path(path), "a").close()
    else:
        log.debug("Deny {0!r}".format(path))
        util.unlink(export_path(path))


def export(config):
    """Walks all repositories owned by :mod:`gitosis`, and manage the
    ``git-daemon-export-ok`` markers.
    """
    global_enable = config.getboolean("gitosis", "daemon")
    log.debug("Global default is {0!r}"
              .format(["allow", "deny"][global_enable]))

    base_dir = config.repository_dir
    for dirpath, dirnames, _ in util.walk(base_dir):
        # Repository path, relative to base repository directory.
        reldir = os.path.relpath(dirpath, base_dir)
        reldir = reldir if reldir != "." else ""

        log.debug("Walking {0!r}, seeing {1!r}".format(reldir, dirnames))

        for dirname in dirnames[:]:
            if not dirname.endswith(".git"):
                continue  # Not a gitosis repository? -- ignore
            else:
                dirnames.remove(dirname)

            # Extract full repository name "foo.git" in directory "./bar"
            # would become "bar/foo".
            repo, _ = os.path.splitext(dirname)
            repo = os.path.join(reldir, repo)

            # Checking if ``gitdaemon`` is enabled for the processed
            # repository.
            enable = config.getboolean("repo {0}".format(repo),
                                       "daemon", default=global_enable)

            # Hardcore action.
            export_one(os.path.join(dirpath, dirname), enable=enable)
