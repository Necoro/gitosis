# -*- coding: utf-8 -*-

import os

from gitosis.config import GitosisRawConfigParser


def test_repository_dir_cfg_missing():
    cfg = GitosisRawConfigParser()
    assert cfg.repository_dir == os.path.expanduser("~/repositories")


def test_repository_dir_cfg_empty():
    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.set("gitosis", "repositories", "")

    assert cfg.repository_dir == os.path.expanduser("~/")


def test_repository_dir_cfg_relative():
    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.set("gitosis", "repositories", "foobar")

    assert cfg.repository_dir == os.path.expanduser("~/foobar")


def test_repository_dir_cfg_absolute():
    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.set("gitosis", "repositories", "/var/gitroot")

    assert cfg.repository_dir == "/var/gitroot"


def test_generated_files_dir_cfg_missing():
    cfg = GitosisRawConfigParser()
    assert cfg.generated_files_dir == os.path.expanduser("~/gitosis")


def test_generated_files_dir_cfg_empty():
    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.set("gitosis", "generate-files-in", "")

    assert cfg.generated_files_dir == ""


def test_generated_files_dir_cfg_set():
    cfg = GitosisRawConfigParser()
    cfg.add_section("gitosis")
    cfg.set("gitosis", "generate-files-in", "foobar")

    assert cfg.generated_files_dir == "foobar"
