"""
Gitosis functions to find what groups a given user belongs to.
"""
import logging
from ConfigParser import NoSectionError, NoOptionError
        
_GROUP_PREFIX = 'group '

def _getMembership(config, user, seen):
    """
    Internal implementation of getMembership.
    Generate groups ``user`` is member of, according to ``config``.
    Groups already seen are tracked by ``seen``.

    :type config: RawConfigParser
    :type user: str
    :type seen: Set
    """
    log = logging.getLogger('gitosis.group.getMembership')

    for section in config.sections():
        if not section.startswith(_GROUP_PREFIX):
            continue
        group = section[len(_GROUP_PREFIX):]
        if group in seen:
            continue

        try:
            members = config.get(section, 'members')
        except (NoSectionError, NoOptionError):
            members = []
        else:
            members = members.split()

        # @all is the only group where membership needs to be
        # bootstrapped like this, anything else gets started from the
        # username itself
        if (user in members
            or '@all' in members):
            log.debug('found %(user)r in %(group)r' % dict(
                user=user,
                group=group,
                ))
            seen.add(group)
            yield group

            for member_of in _getMembership(
                config, '@%s' % group, seen,
                ):
                yield member_of
            for member_of in _getMembership(
                config, '@all', seen,
                ):
                yield member_of

def getMembership(config, user):
    """
    Generate groups ``user`` is member of, according to ``config``

    :type config: RawConfigParser
    :type user: str
    """

    seen = set()
    for member_of in _getMembership(config, user, seen):
        yield member_of

    # everyone is always a member of group "all"
    yield 'all'

