"""
Perform gitosis actions for a git hook.
"""

import logging
import os
import sys

from gitosis import repository
from gitosis import ssh
from gitosis import gitweb
from gitosis import cgit
from gitosis import gitdaemon
from gitosis import app
from gitosis import util

def build_reposistory_data(config):
    """
    Using the ``config`` data, perform all actions that affect files in the .git
    repositories, such as the description, owner, and export marker. Also
    update the projects.list file as needed to list relevant repositories.

    :type config: RawConfigParser
    """
    gitweb.set_descriptions(
        config=config,
        )
    generated = util.getGeneratedFilesDir(config=config)
    gitweb.generate_project_list(
        config=config,
        path=os.path.join(generated, 'projects.list'),
        )
    cgit.generate_project_list(
        config=config,
        path=os.path.join(generated, 'repos.list'),
        )
    gitdaemon.set_export_ok(
        config=config,
        )

def post_update(cfg, git_dir): #pragma: no cover
    """
    post-update hook for the Gitosis admin directory.

    1. Make an export of the admin repo to a clean directory.
    2. Move the gitosis.conf file to it's destination.
    3. Update the repository descriptions.
    4. Update the projects.list file.
    5. Update the repository export markers.
    6. Update the Gitosis SSH keys.
    """
    export = os.path.join(git_dir, 'gitosis-export')
    util.rmtree(export)
    repository.export(git_dir=git_dir, path=export)
    os.rename(
        os.path.join(export, 'gitosis.conf'),
        os.path.join(export, '..', 'gitosis.conf'),
        )
    # re-read config to get up-to-date settings
    cfg.read(os.path.join(export, '..', 'gitosis.conf'))
    build_reposistory_data(cfg)
    authorized_keys = util.getSSHAuthorizedKeysPath(config=cfg)
    ssh.writeAuthorizedKeys(
        path=authorized_keys,
        keydir=os.path.join(export, 'keydir'),
        )

class Main(app.App):
    """gitosis-run-hook program."""
    # W0613 - They also might ignore arguments here, where the descendant
    # methods won't.
    # pylint: disable-msg=W0613

    def create_parser(self):
        """Declare the input for this program."""
        parser = super(Main, self).create_parser()
        parser.set_usage('%prog [OPTS] HOOK')
        parser.set_description(
            'Perform gitosis actions for a git hook')
        return parser

    def handle_args(self, parser, cfg, options, args): #pragma: no cover
        """Parse the input for this program."""
        try:
            (hook,) = args
        except ValueError:
            parser.error('Missing argument HOOK.')

        log = logging.getLogger('gitosis.run_hook')
        os.umask(0022)

        git_dir = os.environ.get('GIT_DIR')
        if git_dir is None:
            log.error('Must have GIT_DIR set in enviroment')
            sys.exit(1)

        if hook == 'post-update':
            log.info('Running hook %s', hook)
            post_update(cfg, git_dir)
            log.info('Done.')
        else:
            log.warning('Ignoring unknown hook: %r', hook)
