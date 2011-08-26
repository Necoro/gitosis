# -*- coding: utf-8 -*-

import os

from gitosis import gitdaemon
from gitosis.config import GitosisRawConfigParser
from gitosis.test.util import maketemp, writeFile


def exported(path):
    """Returns ``True`` if a repository at a given path was exported
    for ``git-daemon`` and ``False`` otherwise.
    """
    return os.path.exists(path) and os.path.exists(gitdaemon.export_path(path))


def test_git_daemon_export_ok_repo_missing():
    # configured but not created yet; before first push
    tmp = maketemp()
    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.set("gitosis", "repositories", tmp)
    cfg.add_section("repo foo")
    cfg.set("repo foo", "daemon", "yes")

    gitdaemon.export(cfg)
    assert not os.path.exists(os.path.join(tmp, "foo"))
    assert not os.path.exists(os.path.join(tmp, "foo.git"))


def test_git_daemon_export_ok_repo_missing_parent():
    # configured but not created yet; before first push
    tmp = maketemp()
    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.set("gitosis", "repositories", tmp)
    cfg.add_section("repo foo/bar")
    cfg.set("repo foo/bar", "daemon", "yes")

    gitdaemon.export(cfg)
    assert not os.path.exists(os.path.join(tmp, "foo"))


def test_git_daemon_export_ok_allowed():
    tmp = maketemp()
    path = os.path.join(tmp, "foo.git")
    os.mkdir(path)

    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.set("gitosis", "repositories", tmp)
    cfg.add_section("repo foo")
    cfg.set("repo foo", "daemon", "yes")

    gitdaemon.export(cfg)
    assert exported(path)


def test_git_daemon_export_ok_allowed_already():
    tmp = maketemp()
    path = os.path.join(tmp, "foo.git")
    os.mkdir(path)
    writeFile(gitdaemon.export_path(path), "")
    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.set("gitosis", "repositories", tmp)
    cfg.add_section("repo foo")
    cfg.set("repo foo", "daemon", "yes")

    gitdaemon.export(cfg)
    assert exported(path)


def test_git_daemon_export_ok_denied():
    tmp = maketemp()
    path = os.path.join(tmp, "foo.git")
    os.mkdir(path)
    writeFile(gitdaemon.export_path(path), "")
    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.set("gitosis", "repositories", tmp)
    cfg.add_section("repo foo")
    cfg.set("repo foo", "daemon", "no")

    gitdaemon.export(cfg)
    assert not exported(path)


def test_git_daemon_export_ok_denied_already():
    tmp = maketemp()
    path = os.path.join(tmp, "foo.git")
    os.mkdir(path)
    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.set("gitosis", "repositories", tmp)
    cfg.add_section("repo foo")
    cfg.set("repo foo", "daemon", "no")

    gitdaemon.export(cfg)
    assert not exported(path)


def test_git_daemon_export_ok_subdirs():
    tmp = maketemp()
    foo = os.path.join(tmp, "foo")
    os.mkdir(foo)
    path = os.path.join(foo, "bar.git")
    os.mkdir(path)
    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.set("gitosis", "repositories", tmp)
    cfg.add_section("repo foo/bar")
    cfg.set("repo foo/bar", "daemon", "yes")

    gitdaemon.export(cfg)
    assert exported(path)


def test_git_daemon_export_ok_denied_default():
    tmp = maketemp()
    path = os.path.join(tmp, "foo.git")
    os.mkdir(path)
    writeFile(gitdaemon.export_path(path), "")
    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.set("gitosis", "repositories", tmp)
    cfg.add_section("repo foo")

    gitdaemon.export(cfg)
    assert not exported(path)


def test_git_daemon_export_ok_denied_even_not_configured():
    # repositories not mentioned in config also get touched; this is
    # to avoid security trouble, otherwise we might expose (or
    # continue to expose) old repositories removed from config
    tmp = maketemp()
    path = os.path.join(tmp, "foo.git")
    os.mkdir(path)
    writeFile(gitdaemon.export_path(path), "")
    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.set("gitosis", "repositories", tmp)

    gitdaemon.export(cfg)
    assert not exported(path)


def test_git_daemon_export_ok_allowed_global():
    tmp = maketemp()

    for repo in ["foo.git", "quux.git", "thud.git"]:
        os.mkdir(os.path.join(tmp, repo))

    # try to provoke an invalid allow
    writeFile(gitdaemon.export_path(os.path.join(tmp, "thud.git")), "")

    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.set("gitosis", "repositories", tmp)
    cfg.set("gitosis", "daemon", "yes")
    cfg.add_section("repo foo")
    cfg.add_section("repo quux")
    # same as default, no effect
    cfg.set("repo quux", "daemon", "yes")
    cfg.add_section("repo thud")
    # this is still hidden
    cfg.set("repo thud", "daemon", "no")

    gitdaemon.export(cfg)
    assert exported(os.path.join(tmp, "foo.git"))
    assert exported(os.path.join(tmp, "quux.git"))
    assert not exported(os.path.join(tmp, "thud.git"))
