"""
Generate ``cgit`` project list based on ``gitosis.conf``.

To plug this into ``cgit``, put in your global config file the
following line::

  include=/path/to/your/repos.list
"""

import os, urllib, logging

from ConfigParser import NoSectionError, NoOptionError

from gitosis import util
from gitosis.configutil import getboolean_default, get_default

field_map={'description':'repo.desc',
           'owner':'repo.owner',
           'readme':'repo.readme',
           }

def generate_project_list_fp(config, fp):
    """
    Generate projects list for ``cgit``.

    :param config: configuration to read projects from
    :type config: RawConfigParser

    :param fp: writable for ``repos.list``
    :type fp: (file-like, anything with ``.write(data)``)
    """
    log = logging.getLogger('gitosis.cgit.generate_projects_list')

    repositories = util.getRepositoryDir(config)

    global_enable = getboolean_default(config, 'gitosis', 'cgit', False)
    grouped_sections={}

    for section in config.sections():
        sectiontitle = section.split(None, 1)
        if not sectiontitle or sectiontitle[0] != 'repo':
            continue

        enable = getboolean_default(config, section, 'cgit', global_enable)

        if not enable:
            continue
        groupname = get_default(config, section, 'cgit_group', "")
        grouped_sections.setdefault(groupname,[]).append(section)

    for groupname, group in grouped_sections.iteritems():
        if groupname:
            print >> fp, 'repo.group=%s'%(groupname)

        for section in group:
            sectiontitle = section.split(None, 1)

            name = sectiontitle[1]

            fullpath = _repository_path(log, repositories, name, name)

            print >> fp, 'repo.url=%s'%(name)

            if fullpath is None:
                continue

            print >> fp, 'repo.path=%s'%(fullpath)

            for field_pair in field_map.iteritems():
                try:
                    field_value = config.get(section, field_pair[0])
                except (NoSectionError, NoOptionError):
                    continue
                else:
                    print >> fp, '%s=%s'%(field_pair[1],field_value)

def _repository_path(log, repositories, name, default_value):
    """
    Check if the repository exists by the common name, or with a .git suffix,
    and return the full pathname.
    """
    fullpath=os.path.join(repositories, name)
    if not os.path.exists(fullpath):
        namedotgit = '%s.git' % name
        fullpath=os.path.join(repositories, namedotgit)
        if os.path.exists(fullpath):
            return fullpath
        else:
            log.warning(
                    'Cannot find %(name)r in %(repositories)r'
                    % dict(name=name, repositories=repositories))
            return None
    return fullpath

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
