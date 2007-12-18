"""
Generate ``gitweb`` project list based on ``gitosis.conf``.

To plug this into ``gitweb``, you have two choices.

- The global way, edit ``/etc/gitweb.conf`` to say::

    $projects_list = "/path/to/your/projects.list";

  Note that there can be only one such use of gitweb.

- The local way, create a new config file::

    do "/etc/gitweb.conf" if -e "/etc/gitweb.conf";
    $projects_list = "/path/to/your/projects.list";
        # see ``repositories`` in the ``gitosis`` section
        # of ``~/.gitosis.conf``; usually ``~/repositories``
        # but you need to expand the tilde here
    $projectroot = "/path/to/your/repositories";

   Then in your web server, set environment variable ``GITWEB_CONFIG``
   to point to this file.

   This way allows you have multiple separate uses of ``gitweb``, and
   isolates the changes a bit more nicely. Recommended.
"""

import os, urllib, logging

from ConfigParser import NoSectionError, NoOptionError

from gitosis import util
from gitosis.configutil import getboolean_default

def _escape_filename(i):
    """Try to make the filename safer."""
    i = i.replace('\\', '\\\\')
    i = i.replace('$', '\\$')
    i = i.replace('"', '\\"')
    return i

def generate_project_list_fp(config, fp):
    """
    Generate projects list for ``gitweb``.

    :param config: configuration to read projects from
    :type config: RawConfigParser

    :param fp: writable for ``projects.list``
    :type fp: (file-like, anything with ``.write(data)``)
    """
    log = logging.getLogger('gitosis.gitweb.generate_projects_list')

    repositories = util.getRepositoryDir(config)

    global_enable = getboolean_default(config, 'gitosis', 'gitweb', False)

    for section in config.sections():
        sectiontitle = section.split(None, 1)
        if not sectiontitle or sectiontitle[0] != 'repo':
            continue

        enable = getboolean_default(config, section, 'gitweb', global_enable)

        if not enable:
            continue

        name = sectiontitle[1]

        name = _repository_exists(log, repositories, name, name)

        response = [name]
        try:
            owner = config.get(section, 'owner')
        except (NoSectionError, NoOptionError):
            pass
        else:
            response.append(owner)

        line = ' '.join([urllib.quote_plus(_) for _ in response])
        print >> fp, line


def _repository_exists(log, repositories, name, default_value):
    """
    Check if the repository exists by the common name, or with a .git suffix,
    and return the relative name.
    """
    if not os.path.exists(os.path.join(repositories, name)):
        namedotgit = '%s.git' % name
        if os.path.exists(os.path.join(repositories, namedotgit)):
            name = namedotgit
        else:
            log.warning(
                    'Cannot find %(name)r in %(repositories)r'
                    % dict(name=name, repositories=repositories))
            return default_value
    return name

def generate_project_list(config, path):
    """
    Generate projects list for ``gitweb``.

    :param config: configuration to read projects from
    :type config: RawConfigParser

    :param path: path to write projects list to
    :type path: str
    """
    tmp = '%s.%d.tmp' % (path, os.getpid())

    fp = file(tmp, 'w')
    try:
        generate_project_list_fp(config=config, fp=fp)
    finally:
        fp.close()

    os.rename(tmp, path)


def set_descriptions(config):
    """
    Set descriptions for gitweb use.
    """
    log = logging.getLogger('gitosis.gitweb.set_descriptions')

    repositories = util.getRepositoryDir(config)

    for section in config.sections():
        sectiontitle = section.split(None, 1)
        if not sectiontitle or sectiontitle[0] != 'repo':
            continue

        try:
            description = config.get(section, 'description')
        except (NoSectionError, NoOptionError):
            continue

        if not description: #pragma: no cover
            continue

        name = sectiontitle[1]

        name = _repository_exists(log, repositories, name, False)
        if not name:
            continue

        path = os.path.join(
            repositories,
            name,
            'description',
            )
        tmp = '%s.%d.tmp' % (path, os.getpid())
        fp = file(tmp, 'w')
        try:
            print >> fp, description
        finally:
            fp.close()
        os.rename(tmp, path)
