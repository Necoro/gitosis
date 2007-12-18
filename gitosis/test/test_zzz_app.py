from nose.tools import eq_ as eq, assert_raises

from gitosis import app
import sys
import os

class TestMain(app.App):
    def handle_args(self, parser, cfg, options, args):
        """Parse the input for this program."""
        pass

def test_app_setup_basic_logging():
    main = TestMain()
    main.setup_basic_logging()

def test_app_create_parser():
    main = TestMain()
    parser = main.create_parser()

def test_app_create_parser_parse_none():
    main = TestMain()
    parser = main.create_parser()
    (options, args) = parser.parse_args([])
    print '%r' % (options, )
    eq(args, [])
    eq(options, {'config': os.path.expanduser('~/.gitosis.conf')})

def test_app_create_parser_parse_config():
    main = TestMain()
    parser = main.create_parser()
    (options, args) = parser.parse_args(['--config=/dev/null'])
    eq(args, [])
    eq(options, {'config': '/dev/null'})

def test_app_create_config():
    main = TestMain()
    cfg = main.create_config(None)

def test_app_read_config_empty():
    main = TestMain()
    cfg = main.create_config(None)
    parser = main.create_parser()
    (options, args) = parser.parse_args(['--config=/dev/null'])
    main.read_config(options, cfg)

def test_app_read_config_does_not_exist():
    main = TestMain()
    cfg = main.create_config(None)
    parser = main.create_parser()
    (options, args) = parser.parse_args(['--config=/does/not/exist'])
    assert_raises(app.ConfigFileDoesNotExistError, main.read_config, options, cfg)


def test_app_setup_logging_default():
    main = TestMain()
    cfg = main.create_config(None)
    main.setup_logging(cfg)

def test_app_setup_logging_goodname():
    main = TestMain()
    cfg = main.create_config(None)
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'loglevel', 'WARN')
    main.setup_logging(cfg)

def test_app_setup_logging_badname():
    main = TestMain()
    cfg = main.create_config(None)
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'loglevel', 'FOOBAR')
    main.setup_logging(cfg)

# We must call this test last
def test_zzz_app_main():
    class Main(TestMain):
        def read_config(self, options, cfg):
            """Ignore errors that result from non-existent config file."""
            pass
    oldargv = sys.argv
    sys.argv = []
    main = Main()
    main.run()
    #parser = self.create_parser()
    #(options, args) = parser.parse_args()
    #cfg = self.create_config(options)
    sys.argv = oldargv
