from nose.tools import eq_ as eq
from gitosis.test.util import assert_raises

import os
from ConfigParser import RawConfigParser

from gitosis import serve
from gitosis import repository

from gitosis.test import util

def test_bad_newLine():
    cfg = RawConfigParser()
    e = assert_raises(
        serve.CommandMayNotContainNewlineError,
        serve.serve,
        cfg=cfg,
        user='jdoe',
        command='ev\nil',
        )
    eq(str(e), 'Command may not contain newline')
    assert isinstance(e, serve.ServingError)

def test_bad_nospace():
    cfg = RawConfigParser()
    e = assert_raises(
        serve.UnknownCommandError,
        serve.serve,
        cfg=cfg,
        user='jdoe',
        command='git-upload-pack',
        )
    eq(str(e), 'Unknown command denied')
    assert isinstance(e, serve.ServingError)

def test_bad_command():
    cfg = RawConfigParser()
    e = assert_raises(
        serve.UnknownCommandError,
        serve.serve,
        cfg=cfg,
        user='jdoe',
        command="evil 'foo'",
        )
    eq(str(e), 'Unknown command denied')
    assert isinstance(e, serve.ServingError)

def test_bad_unsafeArguments():
    cfg = RawConfigParser()
    e = assert_raises(
        serve.UnsafeArgumentsError,
        serve.serve,
        cfg=cfg,
        user='jdoe',
        command='git-upload-pack /evil/attack',
        )
    eq(str(e), 'Arguments to command look dangerous')
    assert isinstance(e, serve.ServingError)

def test_bad_forbiddenCommand_read():
    cfg = RawConfigParser()
    e = assert_raises(
        serve.ReadAccessDenied,
        serve.serve,
        cfg=cfg,
        user='jdoe',
        command="git-upload-pack 'foo'",
        )
    eq(str(e), 'Repository read access denied')
    assert isinstance(e, serve.AccessDenied)
    assert isinstance(e, serve.ServingError)

def test_bad_forbiddenCommand_write_noAccess():
    cfg = RawConfigParser()
    e = assert_raises(
        serve.ReadAccessDenied,
        serve.serve,
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    # error message talks about read in an effort to make it more
    # obvious that jdoe doesn't have *even* read access
    eq(str(e), 'Repository read access denied')
    assert isinstance(e, serve.AccessDenied)
    assert isinstance(e, serve.ServingError)

def test_bad_forbiddenCommand_write_readAccess():
    cfg = RawConfigParser()
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'readonly', 'foo')
    e = assert_raises(
        serve.WriteAccessDenied,
        serve.serve,
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(str(e), 'Repository write access denied')
    assert isinstance(e, serve.AccessDenied)
    assert isinstance(e, serve.ServingError)

def test_simple_read():
    tmp = util.maketemp()
    repository.init(os.path.join(tmp, 'foo.git'))
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'readonly', 'foo')
    got = serve.serve(
        cfg=cfg,
        user='jdoe',
        command="git-upload-pack 'foo'",
        )
    eq(got, "git-upload-pack '%s/foo'" % tmp)

def test_simple_write():
    tmp = util.maketemp()
    repository.init(os.path.join(tmp, 'foo.git'))
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    got = serve.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(got, "git-receive-pack '%s/foo'" % tmp)

def test_push_inits_if_needed():
    # a push to a non-existent repository (but where config authorizes
    # you to do that) will create the repository on the fly
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    serve.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(os.listdir(tmp), ['foo.git'])
    assert os.path.isfile(os.path.join(tmp, 'foo.git', 'HEAD'))

def test_push_inits_if_needed_haveExtension():
    # a push to a non-existent repository (but where config authorizes
    # you to do that) will create the repository on the fly
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    serve.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo.git'",
        )
    eq(os.listdir(tmp), ['foo.git'])
    assert os.path.isfile(os.path.join(tmp, 'foo.git', 'HEAD'))

def test_push_inits_if_needed_existsWithExtension():
    tmp = util.maketemp()
    os.mkdir(os.path.join(tmp, 'foo.git'))
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    serve.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(os.listdir(tmp), ['foo.git'])
    # it should *not* have HEAD here as we just mkdirred it and didn't
    # create it properly, and the mock repo didn't have anything in
    # it.. having HEAD implies serve ran git init, which is supposed
    # to be unnecessary here
    eq(os.listdir(os.path.join(tmp, 'foo.git')), [])

def test_push_inits_no_stdout_spam():
    # git init has a tendency to spew to stdout, and that confuses
    # e.g. a git push
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    old_stdout = os.dup(1)
    try:
        new_stdout = os.tmpfile()
        os.dup2(new_stdout.fileno(), 1)
        serve.serve(
            cfg=cfg,
            user='jdoe',
            command="git-receive-pack 'foo'",
            )
    finally:
        os.dup2(old_stdout, 1)
        os.close(old_stdout)
    new_stdout.seek(0)
    got = new_stdout.read()
    new_stdout.close()
    eq(got, '')
    eq(os.listdir(tmp), ['foo.git'])
    assert os.path.isfile(os.path.join(tmp, 'foo.git', 'HEAD'))