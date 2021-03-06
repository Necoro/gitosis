"""
Enforce git-shell to only serve allowed by access control policy.
directory. The client should refer to them without any extra directory
prefix. Repository names are forced to match ALLOW_RE.
"""

import logging

import sys, os, re

from gitosis import access
from gitosis import repository
from gitosis import app
from gitosis import util
from gitosis import run_hook

log = logging.getLogger('gitosis.serve')

ALLOW_RE = re.compile("^'/*(?P<path>[a-zA-Z0-9][a-zA-Z0-9@._-]*(/[a-zA-Z0-9][a-zA-Z0-9@._-]*)*)'$")

COMMANDS_READONLY = [
    'git-upload-pack',
    'git upload-pack',
    ]

COMMANDS_WRITE = [
    'git-receive-pack',
    'git receive-pack',
    ]

class ServingError(Exception):
    """Serving error"""

    def __str__(self):
        return '%s' % self.__doc__

class CommandMayNotContainNewlineError(ServingError):
    """Command may not contain newline"""

class UnknownCommandError(ServingError):
    """Unknown command denied"""

class UnsafeArgumentsError(ServingError):
    """Arguments to command look dangerous"""

class AccessDenied(ServingError):
    """Access denied to repository"""

class WriteAccessDenied(AccessDenied):
    """Repository write access denied"""

class ReadAccessDenied(AccessDenied):
    """Repository read access denied"""

def serve(cfg, user, command):
    """Check the git command for sanity, and then run the git command."""

    log = logging.getLogger('gitosis.serve.serve')

    if '\n' in command:
        raise CommandMayNotContainNewlineError()

    try:
        verb, args = command.split(None, 1)
    except ValueError:
        # all known "git-foo" commands take one argument; improve
        # if/when needed
        raise UnknownCommandError()

    if verb == 'git':
        try:
            subverb, args = args.split(None, 1)
        except ValueError:
            # all known "git foo" commands take one argument; improve
            # if/when needed
            raise UnknownCommandError()
        verb = '%s %s' % (verb, subverb)

    if (verb not in COMMANDS_WRITE
        and verb not in COMMANDS_READONLY):
        raise UnknownCommandError()

    log.debug('Got command %(cmd)r and args %(args)r' % dict(
                cmd=verb,
                args=args,
                ))

    if args.startswith("'/") and args.endswith("'"):
        args = args[1:-1]
        repos = cfg.repository_dir
        reposreal = os.path.realpath(repos)
        if args.startswith(repos):
            args = os.path.realpath(args)[len(repos)+1:]
        elif args.startswith(reposreal):
            args = os.path.realpath(args)[len(reposreal)+1:]
        else:
            args = args[1:]
        args = "'%s'" % (args, )

    match = ALLOW_RE.match(args)
    if match is None:
        raise UnsafeArgumentsError()

    path = match.group('path')

    # write access is always sufficient
    newpath = access.allowed(
        config=cfg,
        user=user,
        mode='writable',
        path=path)

    if newpath is None:
        # didn't have write access; try once more with the popular
        # misspelling
        newpath = access.allowed(
            config=cfg,
            user=user,
            mode='writeable',
            path=path)
        if newpath is not None:
            log.warning('Repository %r config has typo "writeable", '
                +'should be "writable"',
                path,
                )

    if newpath is None:
        # didn't have write access

        newpath = access.allowed(
            config=cfg,
            user=user,
            mode='readonly',
            path=path)

        if newpath is None:
            raise ReadAccessDenied()

        if verb in COMMANDS_WRITE:
            # didn't have write access and tried to write
            raise WriteAccessDenied()

    (topdir, relpath) = newpath
    assert not relpath.endswith('.git'), \
           'git extension should have been stripped: %r' % relpath
    repopath = '%s.git' % relpath
    fullpath = os.path.join(topdir, repopath)
    if not os.path.exists(fullpath):
        # it doesn't exist on the filesystem, but the configuration
        # refers to it, we're serving a write request, and the user is
        # authorized to do that: create the repository on the fly

        # create leading directories
        path = topdir
        newdirmode = cfg.get('repo %s' % (relpath, ), 'dirmode')
        if newdirmode is None:
            newdirmode = cfg.get('gitosis', 'dirmode', default='0750')

        # Convert string as octal to a number
        newdirmode = int(newdirmode, 8)

        for segment in repopath.split(os.sep)[:-1]:
            path = os.path.join(path, segment)
            util.mkdir(path, newdirmode)

        repository.init(path=fullpath, mode=newdirmode)
        run_hook.build_reposistory_data(cfg)

    # put the verb back together with the new path
    newcmd = "%(verb)s '%(path)s'" % dict(
        verb=verb,
        path=fullpath,
        )
    return newcmd

class Main(app.App):
    """gitosis-serve program."""
    # W0613 - They also might ignore arguments here, where the descendant
    # methods won't.
    # pylint: disable-msg=W0613

    def create_parser(self):
        """Declare the input for this program."""
        parser = super(Main, self).create_parser()
        parser.set_usage('%prog [OPTS] USER')
        parser.set_description(
            'Allow restricted git operations under DIR')
        return parser

    def handle_args(self, parser, cfg, options, args): #pragma: no cover
        """Parse the input for this program."""
        try:
            (user,) = args
        except ValueError:
            parser.error('Missing argument USER.')

        main_log = logging.getLogger('gitosis.serve.main')
        os.umask(0022)

        os.environ['GITOSIS_USER'] = user

        userfile=os.path.join(cfg.repository_dir,'gitosis-admin.git','gitosis-export','keydir',user+'.pub')
        try:
            userdata=open(userfile, 'r').readline()
        except:
            # don't fail if file is not found
            userdata=""

        if len(userdata) > 0:
            m=re.search("^# gitosis-identity: *([^\<]+)? *(?:\<([^\>, ]*)\>)?",userdata)
            if m:
                os.environ['GITOSIS_NAME'] = m.group(1).strip()
                os.environ['GITOSIS_EMAIL'] = m.group(2)
            else:
                m=re.search("^# gitosis-name: *(.*)$", userdata)
                if m:
                    os.environ['GITOSIS_NAME'] = m.group(1).strip()
                m=re.search("^# gitosis-email: *<?(.*)>?$", userdata)
                if m:
                    os.environ['GITOSIS_EMAIL'] = m.group(1).strip()

        cmd = os.environ.get('SSH_ORIGINAL_COMMAND', None)
        if cmd is None:
            main_log.error('Need SSH_ORIGINAL_COMMAND in environment.')
            sys.exit(1)

        main_log.debug('Got command %(cmd)r' % dict(
            cmd=cmd,
            ))

        os.chdir(os.path.expanduser('~'))

        try:
            newcmd = serve(
                cfg=cfg,
                user=user,
                command=cmd,
                )
        except ServingError, e:
            main_log.error('%s', e)
            sys.exit(1)

        main_log.debug('Serving %s', newcmd)
        os.execvp('git', ['git', 'shell', '-c', newcmd])
        main_log.error('Cannot execute git-shell.')
        sys.exit(1)
