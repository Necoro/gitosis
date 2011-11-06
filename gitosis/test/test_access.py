# -*- coding: utf-8 -*-

from gitosis import access
from gitosis.config import GitosisRawConfigParser


def test_write_no_simple():
    cfg = GitosisRawConfigParser()
    assert access.allowed(cfg,
        user="jdoe", mode="writable", path="foo/bar") is None


def test_write_yes_simple():
    cfg = GitosisRawConfigParser()
    cfg.add_section("group fooers")
    cfg.set("group fooers", "members", "jdoe")
    cfg.set("group fooers", "writable", "foo/bar")

    assert access.allowed(cfg,
        user="jdoe", mode="writable", path="foo/bar") == ("repositories", "foo/bar")


def test_write_no_simple_with_readonly():
    cfg = GitosisRawConfigParser()
    cfg.add_section("group fooers")
    cfg.set("group fooers", "members", "jdoe")
    cfg.set("group fooers", "readonly", "foo/bar")

    assert access.allowed(cfg,
        user="jdoe", mode="writable", path="foo/bar") is None


def test_write_yes_map():
    cfg = GitosisRawConfigParser()
    cfg.add_section("group fooers")
    cfg.set("group fooers", "members", "jdoe")
    cfg.set("group fooers", "map writable foo/bar", "quux/thud")

    assert access.allowed(config=cfg,
        user="jdoe", mode="writable", path="foo/bar") == ("repositories", "quux/thud")


def test_write_no_map_with_readonly():
    cfg = GitosisRawConfigParser()
    cfg.add_section("group fooers")
    cfg.set("group fooers", "members", "jdoe")
    cfg.set("group fooers", "map readonly foo/bar", "quux/thud")

    assert access.allowed(cfg,
        user="jdoe", mode="writable", path="foo/bar") is None


def test_read_no_simple():
    cfg = GitosisRawConfigParser()
    assert access.allowed(cfg,
        user="jdoe", mode="readonly", path="foo/bar") is None


def test_read_yes_simple():
    cfg = GitosisRawConfigParser()
    cfg.add_section("group fooers")
    cfg.set("group fooers", "members", "jdoe")
    cfg.set("group fooers", "readonly", "foo/bar")

    assert access.allowed(cfg,
        user="jdoe", mode="readonly", path="foo/bar") == ("repositories", "foo/bar")


def test_read_yes_simple_with_writable():
    cfg = GitosisRawConfigParser()
    cfg.add_section("group fooers")
    cfg.set("group fooers", "members", "jdoe")
    cfg.set("group fooers", "writable", "foo/bar")

    assert access.allowed(config=cfg,
        user="jdoe", mode="readonly", path="foo/bar") is None


def test_read_yes_map():
    cfg = GitosisRawConfigParser()
    cfg.add_section("group fooers")
    cfg.set("group fooers", "members", "jdoe")
    cfg.set("group fooers", "map readonly foo/bar", "quux/thud")

    assert access.allowed(cfg,
        user="jdoe", mode="readonly", path="foo/bar") == ("repositories", "quux/thud")


def test_read_yes_map_with_writable():
    cfg = GitosisRawConfigParser()
    cfg.add_section("group fooers")
    cfg.set("group fooers", "members", "jdoe")
    cfg.set("group fooers", "map writable foo/bar", "quux/thud")

    assert access.allowed(cfg,
        user="jdoe", mode="readonly", path="foo/bar") is None


def test_read_yes_all():
    cfg = GitosisRawConfigParser()
    cfg.add_section("group fooers")
    cfg.set("group fooers", "members", "@all")
    cfg.set("group fooers", "readonly", "foo/bar")

    assert access.allowed(cfg,
        user="jdoe", mode="readonly", path="foo/bar") == ("repositories", "foo/bar")


def test_base_global_absolute():
    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.set("gitosis", "repositories", "/a/leading/path")
    cfg.add_section("group fooers")
    cfg.set("group fooers", "members", "jdoe")
    cfg.set("group fooers", "map writable foo/bar", "baz/quux/thud")

    assert access.allowed(cfg,
        user="jdoe", mode="writable", path="foo/bar") == ("/a/leading/path", "baz/quux/thud")


def test_base_global_relative():
    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.set("gitosis", "repositories", "some/relative/path")
    cfg.add_section("group fooers")
    cfg.set("group fooers", "members", "jdoe")
    cfg.set("group fooers", "map writable foo/bar", "baz/quux/thud")

    assert access.allowed(cfg,
        user="jdoe", mode="writable", path="foo/bar") == ("some/relative/path", "baz/quux/thud")


def test_base_global_relative_simple():
    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.set("gitosis", "repositories", "some/relative/path")
    cfg.add_section("group fooers")
    cfg.set("group fooers", "members", "jdoe")
    cfg.set("group fooers", "readonly", "foo xyzzy bar")

    assert access.allowed(cfg,
        user="jdoe", mode="readonly", path="xyzzy") == ("some/relative/path", "xyzzy")


def test_base_global_unset():
    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.add_section("group fooers")
    cfg.set("group fooers", "members", "jdoe")
    cfg.set("group fooers", "readonly", "foo xyzzy bar")

    assert access.allowed(cfg,
        user="jdoe", mode="readonly", path="xyzzy") == ("repositories", "xyzzy")


def test_base_local():
    cfg = GitosisRawConfigParser()
    cfg.add_section("group fooers")
    cfg.set("group fooers", "repositories", "some/relative/path")
    cfg.set("group fooers", "members", "jdoe")
    cfg.set("group fooers", "map writable foo/bar", "baz/quux/thud")

    assert access.allowed(cfg,
        user="jdoe", mode="writable", path="foo/bar") == ("some/relative/path", "baz/quux/thud")


def test_dotgit():
    # a .git extension is always allowed to be added
    cfg = GitosisRawConfigParser()
    cfg.add_section("group fooers")
    cfg.set("group fooers", "members", "jdoe")
    cfg.set("group fooers", "writable", "foo/bar")

    assert access.allowed(cfg,
        user="jdoe", mode="writable", path="foo/bar.git") == ("repositories", "foo/bar")


def test_owner_full_access():
    cfg = GitosisRawConfigParser()
    cfg.add_section("repo foo/bar")
    cfg.set("repo foo/bar", "owner", "jdoe")

    assert access.allowed(cfg,
        user="jdoe", mode="writable", path="foo/bar") == ("repositories", "foo/bar")

    assert access.allowed(cfg,
        user="jdoe", mode="readable", path="foo/bar") == ("repositories", "foo/bar")

