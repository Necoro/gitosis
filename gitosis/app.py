"""Common code for all callable Gitosis programs."""
import os
import sys
import logging
import optparse
import errno
import ConfigParser

# C0103 - 'log' is a special name
# pylint: disable-msg=C0103
log = logging.getLogger('gitosis.app')

class CannotReadConfigError(Exception):
    """Unable to read config file"""

    def __str__(self):
        return '%s: %s' % (self.__doc__, ': '.join(self.args))

class ConfigFileDoesNotExistError(CannotReadConfigError):
    """Configuration does not exist"""

class App(object):
    """Common Gitosis Application runner."""
    # R0201 - the many of the methods in this class are intended to be
    # overridden, hence they are not suited to be functions.
    # W0613 - They also might ignore arguments here, where the descendant
    # methods won't.
    # pylint: disable-msg=R0201,W0613

    name = None

    def run(cls):
        """Launch the app."""
        app = cls()
        return app.main()
    run = classmethod(run)

    def main(self):
        """Main program routine."""
        self.setup_basic_logging()
        parser = self.create_parser()
        (options, args) = parser.parse_args()
        cfg = self.create_config(options)
        try:
            self.read_config(options, cfg)
        except CannotReadConfigError, ex:
            log.error(str(ex))
            sys.exit(1)
        self.setup_logging(cfg)
        self.handle_args(parser, cfg, options, args)

    def setup_basic_logging(self):
        """Set up the initial logging."""
        logging.basicConfig()

    def create_parser(self):
        """Handle commandline option parsing."""
        parser = optparse.OptionParser()
        parser.set_defaults(
            config=os.path.expanduser('~/.gitosis.conf'),
            )
        parser.add_option('--config',
                          metavar='FILE',
                          help='read config from FILE',
                          )

        return parser

    def create_config(self, options):
        """Handle config file parsing."""
        cfg = ConfigParser.RawConfigParser()
        return cfg

    def read_config(self, options, cfg):
        """Read the configuration file into the config parser."""
        try:
            conffile = file(options.config)
        except (IOError, OSError), ex:
            if ex.errno == errno.ENOENT:
                # special case this because gitosis-init wants to
                # ignore this particular error case
                raise ConfigFileDoesNotExistError(str(ex))
            else:
                raise CannotReadConfigError(str(ex)) #pragma: no cover
        try:
            cfg.readfp(conffile)
        finally:
            conffile.close()

    def setup_logging(self, cfg):
        """Set up the full logging, using the configuration."""
        try:
            loglevel = cfg.get('gitosis', 'loglevel')
        except (ConfigParser.NoSectionError,
                ConfigParser.NoOptionError):
            pass
        else:
            try:
                # logging really should declare the symbolics
                # pylint: disable-msg=W0212
                symbolic = logging._levelNames[loglevel]
            except KeyError:
                log.warning(
                    'Ignored invalid loglevel configuration: %r',
                    loglevel,
                    )
            else:
                logging.root.setLevel(symbolic)

    def handle_args(self, parser, cfg, options, args): #pragma: no cover
        """Abstract method for the non-option argument handling."""
        if args:
            parser.error('not expecting arguments')
