# -*- coding: utf-8 -*-
"""
    gitosis.cgit
    ~~~~~~~~~~~~

    A module which implemets functions for generating
    `cgit <http://hjemli.net/git/cgit>`_ project list, based on the
    contents of ``gitosis.conf``.

    To plug this into `cgit`, put the following into your ``.cgitrc``::

      include=/path/to/your/repos.list

    :license: GPL
"""

from __future__ import with_statement

import logging
import os
import operator
from cStringIO import StringIO
from ConfigParser import NoSectionError, NoOptionError
from functools import partial

from gitosis import util
from gitosis.configutil import getboolean_default, get_default


#: A mapping of fields from ``gitosis.conf`` to fields in
#: ``project.list``.
optional_fields = {"description": "repo.desc",
                   "owner": "repo.owner",
                   "readme": "repo.readme",
                   "filter": "repo.source-filter",
                   "defbranch": "repo.defbranch"}


def get_repositories(config):
    """Returns a mapping of gitosis repositories, grouped by ``cgit_group``."""
    repos = {}  # Grouped by ``cgit_group``.
    global_enable = getboolean_default(config, "gitosis", "cgit", False)

    for section in config.sections():
        data = section.split(" ", 1)
        if not data or data[0] != "repo":
            continue

        if not getboolean_default(config, section, "cgit", global_enable):
            continue

        cgit_group = get_default(config, section, "cgit_group", "")
        cgit_name  = get_default(config, section, "cgit_name", data[1])
        repos.setdefault(cgit_group, []).append((cgit_name, section))
    else:
        return repos.iteritems()


def generate_project(name, section, buf, config):
    log = logging.getLogger("gitosis.cgit.generate_project")

    _, path = section.split(" ", 1)
    base_path = util.getRepositoryDir(config)

    # ``gitsis`` requires all repositories to have a .git suffix.
    if not path.endswith(".git"):
        path += ".git"

    if not os.path.exists(os.path.join(base_path, path)):
        log.debug("Repo {0} doesn't exist @ {1}.".format(path, base_path))
        return

    repo = {
        "repo.url": path,
        "repo.name": name,
        "repo.path": os.path.join(base_path, path),
    }

    # Now add optional fields if any is available ...
    for name in optional_fields:
        try:
            value = config.get(section, name)
        except (NoSectionError, NoOptionError):
            pass
        else:
            repo[optional_fields.get(name)] = value

    # ... and write everything to the buffer.
    for item in repo.iteritems():
        buf.write("{0}={1}".format(*item) + os.linesep)
    else:
        buf.write(os.linesep)


def generate_project_list(config, path):
    log = logging.getLogger("gitosis.cgit.generate_project_list")
    log.debug("Generating `repos.list` file @ {0}.".format(path))
    buf = StringIO()  # Write to a temporary buffer.

    for cgit_group, repos in get_repositories(config):
        log.debug("Found {0!r} for cgit group {1!r}."
                  .format(map(operator.itemgetter(0), repos), cgit_group))
        if cgit_group:
            buf.write("section={0}".format(cgit_group) +
                      os.linesep)
            buf.write(os.linesep)

        map(lambda (name, section): generate_project(name,
                                                     section,
                                                     buf, config),
            repos)

    log.debug("Saving to {0} ...".format(path))
    with open(path, "w") as fp:
        fp.write(buf.getvalue())
        fp.close()
    log.debug("Done.")


logging.basicConfig()
