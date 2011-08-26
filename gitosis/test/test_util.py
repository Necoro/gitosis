# -*- coding: utf-8 -*-

import os
import errno

from nose.tools import eq_ as eq, assert_raises

from gitosis import util
from gitosis.config import GitosisRawConfigParser


def test_catch():
    def foo():
        raise OSError(errno.EEXIST)
    assert_raises(OSError, util.catch(foo, [errno.ENOENT]))


def test_getRepositoryDir_cfg_missing():
    cfg = GitosisRawConfigParser()
    d = util.getRepositoryDir(cfg)
    eq(d, os.path.expanduser('~/repositories'))


def test_getRepositoryDir_cfg_empty():
    cfg = GitosisRawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', '')
    d = util.getRepositoryDir(cfg)
    eq(d, os.path.expanduser('~/'))


def test_getRepositoryDir_cfg_relative():
    cfg = GitosisRawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', 'foobar')
    d = util.getRepositoryDir(cfg)
    eq(d, os.path.expanduser('~/foobar'))


def test_getRepositoryDir_cfg_absolute():
    cfg = GitosisRawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', '/var/gitroot')
    d = util.getRepositoryDir(cfg)
    eq(d, '/var/gitroot')


def test_getGeneratedFilesDir_cfg_missing():
    cfg = GitosisRawConfigParser()
    d = util.getGeneratedFilesDir(cfg)
    eq(d, os.path.expanduser('~/gitosis'))

def test_getGeneratedFilesDir_cfg_empty():
    cfg = GitosisRawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'generate-files-in', '')
    d = util.getGeneratedFilesDir(cfg)
    eq(d, '')

def test_getGeneratedFilesDir_cfg_set():
    cfg = GitosisRawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'generate-files-in', 'foobar')
    d = util.getGeneratedFilesDir(cfg)
    eq(d, 'foobar')
