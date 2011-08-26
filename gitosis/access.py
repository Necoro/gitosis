# -*- coding: utf-8 -*-
"""
    gitosis.access
    ~~~~~~~~~~~~~~

    This module implements access control functions for :mod:`gitosis`.

    :license: GPL
"""

import os
import logging

from gitosis import group as _group


def get_repository_prefix(config, group = None):
    if group:
        # do we have a specific repositories directory for this group?
        prefix = config.get("group {0}".format(group), "repositories")
    else:
        prefix = None

    # if not, try to use the one from 'gitosis' section.
    prefix = prefix or \
        config.get("gitosis", "repositories", default="repositories")
    # or just use the fallback value
    return prefix or "repositories"


def allowed(config, user, mode, path):
    """Check if a user is allowed to access a given path.

    Returns ``None`` for no access, or a tuple of toplevel directory
    containing repositories and a relative path to the physical
    repository.

    :param config: ``gitosis`` config object
    :param str user: a user to check access rights for
    :param str mode: access `readonly` or `writable`
    :param str path: name of the repository to check access
                     rights for (this is what you write in ``[repo ... ]``
                     section of your ``gitosis.conf``)
    """
    log = logging.getLogger("gitosis.access.allowed")
    log.debug("Access check for {0} as {1} on {2}...".format(user, mode, path))

    basename, ext = os.path.splitext(path)
    if ext == ".git":
        log.debug("Stripped `.git` suffix from {0}, new value {1}."
                  .format(path, basename))
        path = basename

    # a) first check if a user is an owner of the repository
    #    == has unlimited access.
    owner = config.get("repo {0}".format(path), "owner")
    if owner and owner == user:
        log.debug("Acces ok for {0!r} as {1!r} on {2!r} (owner)"
                  .format(user, mode, path))
        return get_repository_prefix(config), path

    # b) iterate over user's groups and check if it has requested
    #    pass in any of the sections.
    ok = False
    for group in _group.getMembership(config=config, user=user):
        repos = config.get("group {0}".format(group), mode, default="").split()
        if path in repos:
            log.debug("Access ok for {0!r} as {1!r} on {2!r}"
                      .format(user, mode, path))
            ok = True
        elif os.path.join(os.path.dirname(path), "*") in repos:
            log.debug("Wildcard access ok for {0!r} as {1!r} on {2!r}"
                      .format(user, mode, path))
            ok = True
        else:
            mapping = config.get("group {0}".format(group),
                                 "map {0} {1}".format(mode, path))

            if mapping:
                log.debug("Access ok for {0!r} as {1!r} on {2!r}={3!r}"
                          .format(user, mode, path, mapping))
                ok, path = True, mapping

        if ok:
            prefix = get_repository_prefix(config, group)
            log.debug("Using prefix {0!r}for {1!r}".format(prefix, path))
            return prefix, path


# Compatibility.
haveAccess = allowed
