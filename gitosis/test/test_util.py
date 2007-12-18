from nose.tools import eq_ as eq, assert_raises

import os
import errno

from ConfigParser import RawConfigParser

from gitosis import util

# Nose interferes with this test case, and 'except' block inside _sysfunc does
# not recieve the error.
#def test_sysfunc_raise_ignore():
#    def foo():
#        os.mkdir('/does/not/exist/anywhere')
#    util._sysfunc(foo, [errno.EEXIST])

def test_sysfunc_raise_catch():
    def foo():
        raise OSError(errno.EEXIST)
    assert_raises(OSError, util._sysfunc, foo, [errno.ENOENT])

def test_getRepositoryDir_cfg_missing():
    cfg = RawConfigParser()
    d = util.getRepositoryDir(cfg)
    eq(d, os.path.expanduser('~/repositories'))

def test_getRepositoryDir_cfg_empty():
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', '')
    d = util.getRepositoryDir(cfg)
    eq(d, os.path.expanduser('~/'))

def test_getRepositoryDir_cfg_relative():
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', 'foobar')
    d = util.getRepositoryDir(cfg)
    eq(d, os.path.expanduser('~/foobar'))

def test_getRepositoryDir_cfg_absolute():
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', '/var/gitroot')
    d = util.getRepositoryDir(cfg)
    eq(d, '/var/gitroot')
