"""
Useful wrapper functions to access ConfigParser structures.
"""
from ConfigParser import NoSectionError, NoOptionError, RawConfigParser
from UserDict import IterableUserDict

def getboolean_default(config, section, option, default_value):
    """
    Return the given section.variable, or return the default if no specific
    value is set.
    """
    try:
        value = config.getboolean(section, option)
    except (NoSectionError, NoOptionError):
        value = default_value
    return value
def get_default(config, section, option, default_value):
    """
    Return the given section.variable, or return the default if no specific
    value is set.
    """
    try:
        value = config.get(section, option)
    except (NoSectionError, NoOptionError):
        value = default_value
    return value

class GitosisConfigDict(IterableUserDict):
    def keys(self):
        return list(self.__iter__())
    def __iter__(self):
        saw = set()
        if 'gitosis' in self.data:
            saw.add('gitosis')
            yield 'gitosis'
        sorted_keys = self.data.keys()
        sorted_keys.sort()
        for _ in sorted_keys:
            if _.startswith('group '):
                saw.add(_)
                yield _
        for _ in sorted_keys:
            if _.startswith('repo '):
                saw.add(_)
                yield _
        for _ in sorted_keys:
            if _ not in saw:
                saw.add(_)
                yield _
    

class GitosisRawConfigParser(RawConfigParser):
    def __init__(self, defaults=None):
        RawConfigParser.__init__(self, defaults)
        self._sections = GitosisConfigDict(self._sections)

