import logging
from logging.handlers import RotatingFileHandler
from subprocess import CalledProcessError
from tempfile import NamedTemporaryFile

from mock import patch

from common_test_base import CommonTestBase
from utility import (
    run_shell_command,
    setup_logging,
)


class TestUtility(CommonTestBase):

    def setUp(self):
        self.setup_test_logging()

    def test_run_shell_command(self):
        with patch('utility.check_output', autospec=True) as mock:
            run_shell_command('foo')
        mock.assert_called_once_with(['foo'])

    def test_run_shell_command_error(self):
        with self.assertRaisesRegexp(CalledProcessError, ""):
            run_shell_command('ls -W', quiet_mode=False)

    def test_run_shell_command_output(self):
        output = run_shell_command('echo "hello"')
        self.assertEqual(output, '"hello"\n')

    def test_setup_logging(self):
        with NamedTemporaryFile() as temp_file:
            setup_logging(temp_file.name, log_count=1)
        logger = logging.getLogger()
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(logger.name, 'root')
        handlers = logger.handlers
        self.assertIn(
            type(handlers[0]), [RotatingFileHandler, logging.StreamHandler])
        self.assertIn(
            type(handlers[1]), [RotatingFileHandler, logging.StreamHandler])

    def test_setup_logging_formatter(self):
        log_count = 1
        with NamedTemporaryFile() as temp_file:
            with patch('logging.Formatter') as l_mock:
                setup_logging(temp_file.name, log_count=log_count)
        logger = logging.getLogger()
        self.assertEqual(logger.name, 'root')
        l_mock.assert_called_once_with(
            '%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S')

    def test_setup_logging_rotating_file_handler(self):
        log_count = 1
        with NamedTemporaryFile() as temp_file:
            with patch('utility.RotatingFileHandler') as mock:
                setup_logging(temp_file.name, log_count=log_count)
        mock.assert_called_once_with(
            temp_file.name, maxBytes=1024 * 1024 * 512, backupCount=log_count)

    def test_log(self):
        with NamedTemporaryFile() as temp_file:
            setup_logging(temp_file.name, log_count=1)
            logging.info('testing123')
            with open(temp_file.name, 'r') as file_reader:
                content = file_reader.read()
                # log format: 2015-04-29 14:03:02 INFO testing123
                match = content.split(' ', 2)[2]
                self.assertEqual(match, 'INFO testing123\n')

    def test_log_debug(self):
        with NamedTemporaryFile() as temp_file:
            setup_logging(temp_file.name, log_count=1)
            logging.debug("testing123")
            with open(temp_file.name, 'r') as file_reader:
                content = file_reader.read()
                # log format: 2015-04-29 14:03:02 INFO testing123
                match = content.split(' ', 2)[2]
                self.assertEqual(match, 'DEBUG testing123\n')

    def test_log_error(self):
        with NamedTemporaryFile() as temp_file:
            setup_logging(temp_file.name, log_count=1)
            logging.error("testing123")
            with open(temp_file.name, 'r') as file_reader:
                content = file_reader.read()
                # log format: 2015-04-29 14:03:02 INFO testing123
                match = content.split(' ', 2)[2]
                self.assertEqual(match, 'ERROR testing123\n')
