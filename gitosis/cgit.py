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
import re
import subprocess
from cStringIO import StringIO


#: A mapping of fields from ``gitosis.conf`` to fields in
#: ``project.list``.
optional_fields = {"description": "repo.desc",
                   "owner": "repo.owner",
                   "readme": "repo.readme",
                   "filter": "repo.source-filter",
                   "defbranch": "repo.defbranch"}


def find_repositories(config):
    """Returns a mapping of gitosis repositories, grouped by ``cgit_group``."""
    repos = {}  # Grouped by ``cgit_group``.
    global_enable = config.getboolean("gitosis", "cgit", default=False)

    for section in config.sections():
        data = section.split(" ", 1)
        if not data or data[0] != "repo":
            continue

        if not config.getboolean(section, "cgit", default=global_enable):
            continue

        cgit_group = config.get(section, "cgit_group", default="")
        cgit_name  = config.get(section, "cgit_name", default=data[1])
        repos.setdefault(cgit_group, []).append((cgit_name, section))
    else:
        return repos.iteritems()


def find_readme(path, treeish="master"):
    git = subprocess.Popen(["git", "ls-tree",
                            "-r",  # Recurse into subdirectories.
                            "--name-only",
                            treeish],
                            cwd=path,
                            env={"GIT_DIR": path},
                            stdout=subprocess.PIPE,
                            close_fds=True)

    for fname in git.stdout.read().splitlines():
        if re.match("(?i)readme", fname):
            # The latest version of ``cgit`` seems to refuse readme
            # without refspec.
            return "{0}:{1}".format(treeish, fname)


def generate_project(name, section, buf, config):
    log = logging.getLogger("gitosis.cgit.generate_project")

    _, path = section.split(" ", 1)
    base_path = config.repository_dir

    # ``gitsis`` requires all repositories to have a .git suffix.
    if not path.endswith(".git"):
        path += ".git"

    if not os.path.exists(os.path.join(base_path, path)):
        log.debug("Repo {0} doesn't exist @ {1}.".format(path, base_path))
        return

    repo = [
        ("repo.url", path),
        ("repo.name", name),
        ("repo.path", os.path.join(base_path, path)),
    ]

    # Now add optional fields if any is available ...
    for name in optional_fields:
        value = config.get(section, name)
        if not value:
            # If readme is not explicitly given, try to guess it.
            if name == "readme":
                value = find_readme(os.path.join(base_path, path))
            else:
                continue

        if value:
            repo.append((optional_fields[name], value))

    # ... and write everything to the buffer.
    for item in repo:
        buf.write("{0}={1}".format(*item) + os.linesep)
    else:
        buf.write(os.linesep)


def generate_project_list(config, path):
    log = logging.getLogger("gitosis.cgit.generate_project_list")
    log.debug("Generating `repos.list` file @ {0}.".format(path))
    buf = StringIO()  # Write to a temporary buffer.

    for cgit_group, repos in find_repositories(config):
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
