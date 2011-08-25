# -*- coding: utf-8 -*-
"""
    gitosis.config
    ~~~~~~~~~~~~~~

    This module implements a tiny wrapper around
    :class:`~ConfigParser.ConfigParser` -- because raw `ConfigParser`
    is barely usable.

    :license: GPL
"""

from ConfigParser import NoSectionError, NoOptionError, RawConfigParser
from UserDict import IterableUserDict


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

    def get(self, section, option, default=None):
        """Same as :meth:`dict.get` but for
        :class:`~ConfigParser.ConfigParser` instances."""
        try:
            return RawConfigParser.get(self, section, option)
        except (NoSectionError, NoOptionError):
            return default

    def getboolean(self, section, option, default=False):
        try:
            return RawConfigParser.getboolean(self, section, option)
        except (ValueError, AttributeError):
            return default

    # FIXME: add getfloat() and getint() with default value.
