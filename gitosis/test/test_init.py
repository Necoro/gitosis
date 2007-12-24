from nose.tools import eq_ as eq
from gitosis.test.util import assert_raises, maketemp

import os

from gitosis import init
from gitosis import repository
from gitosis.configutil import GitosisRawConfigParser

from gitosis.test import util

def test_init_admin_repository():
    tmp = maketemp()
    admin_repository = os.path.join(tmp, 'admin.git')
    pubkey = (
        'ssh-somealgo '
        +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fakeuser@fakehost')
    user = 'jdoe'
    cfg = GitosisRawConfigParser()
    init.init_admin_repository(
        git_dir=admin_repository,
        pubkey=pubkey,
        user=user,
        config=cfg,
        )
    eq(os.listdir(tmp), ['admin.git'])
    hook = os.path.join(
        tmp,
        'admin.git',
        'hooks',
        'post-update',
        )
    util.check_mode(hook, 0755, is_file=True)
    got = util.readFile(hook).splitlines()
    assert 'gitosis-run-hook post-update' in got
    export_dir = os.path.join(tmp, 'export')
    repository.export(git_dir=admin_repository,
                      path=export_dir)
    eq(sorted(os.listdir(export_dir)),
       sorted(['gitosis.conf', 'keydir']))
    eq(os.listdir(os.path.join(export_dir, 'keydir')),
       ['jdoe.pub'])
    got = util.readFile(
        os.path.join(export_dir, 'keydir', 'jdoe.pub'))
    eq(got, pubkey)
    # the only thing guaranteed of initial config file ordering is
    # that [gitosis] is first
    got = util.readFile(os.path.join(export_dir, 'gitosis.conf'))
    # We can't gaurentee this anymore
    got = got.splitlines()[0]
    eq(got, '[gitosis]')
    cfg.read(os.path.join(export_dir, 'gitosis.conf'))
    eq(sorted(cfg.sections()),
       sorted([
        'gitosis',
        'group gitosis-admin',
        ]))
    eq(cfg.items('gitosis'), [])
    eq(sorted(cfg.items('group gitosis-admin')),
       sorted([
        ('writable', 'gitosis-admin'),
        ('members', 'jdoe'),
        ]))
