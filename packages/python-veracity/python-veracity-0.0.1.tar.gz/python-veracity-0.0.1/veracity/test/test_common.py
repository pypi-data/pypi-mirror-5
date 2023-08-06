#!/usr/bin/env python

"""
Unit tests for the veracity.common module.
"""

import unittest

import os
import tempfile

from veracity.common import Config, parse_config, find_config

from veracity.test import FILES


class TestModule(unittest.TestCase):  # pylint: disable=R0904
    """Tests for the common module."""  # pylint: disable=C0103

    @staticmethod
    def error(msg):
        """Error function to pass to the config parser."""
        raise Exception(msg)

    def test_find_config_found(self):
        """Verify a config can be found in this project."""
        self.assertTrue(os.path.isfile(find_config(FILES)))

    def test_find_config_not_found(self):
        """Verify None is returned when no config is found."""
        self.assertIsNone(find_config(tempfile.gettempdir()))

    def test_parse_config_valid(self):
        """Verify a config can be parsed."""
        config = parse_config(os.path.join(FILES, 'setup.cfg'), self.error)
        self.assertEqual(['python-veracity-test'], config.repos)

    def test_parse_config_invalid(self):
        """Verify an error occurs when no config is found."""
        self.assertRaises(Exception, parse_config, tempfile.gettempdir(), self.error)


class TestConfig(unittest.TestCase):  # pylint: disable=R0904
    """Tests for the Config class."""  # pylint: disable=C0103

    @classmethod
    def setUpClass(cls):
        cls.config = Config(os.path.join(FILES, 'setup.cfg'))

    def test_override(self):
        """Verify a configuration options can be overridden."""
        config = Config(os.path.join(FILES, 'setup.cfg'),
                        repos=['r1', 'r2'], series=['s1', 's2'], envs=['e1', 'e2'])
        self.assertEqual(['r1', 'r2'], config.repos)
        self.assertEqual(['s1', 's2'], config.series)
        self.assertEqual(['e1', 'e2'], config.environments)

    def test_no_override(self):
        """Verify a configuration options cannot be overridden with empty items."""
        config = Config(os.path.join(FILES, 'setup.cfg'),
                        repos=[], series=[], envs=[])
        self.assertEqual(['python-veracity-test'], config.repos)
        self.assertEqual(['N', 'C'], config.series)
        self.assertEqual(['W', 'M', 'L'], config.environments)

    def test_starts(self):
        """Verify starts can be read from a config."""
        self.assertEqual(['Q', 'Q2'], self.config.starts)

    def test_starts_default(self):
        """Verify default starts can be read from an empty config."""
        config = Config()
        self.assertEqual(['Q'], config.starts)

    def test_ends(self):
        """Verify sends can be read from a config."""
        self.assertEqual(['CF', 'BF', 'D', 'UF', 'TF'], self.config.ends)

    def test_fails(self):
        """Verify fails can be read from a config."""
        self.assertEqual(['CF', 'BF', 'UF', 'TF'], self.config.fails)

    def test_enter_valid(self):
        """Verify a valid state can be entered."""
        self.assertEqual('B', self.config.enter('UP'))

    def test_enter_invalid(self):
        """Verify an invalid state is re-entered."""
        self.assertEqual('FAKE', self.config.enter('FAKE'))

    def test_fail(self):
        """Verify a a state can be failed."""
        self.assertEqual('UF', self.config.fail('U'))

    def test_exit(self):
        """Verify a a state can be exited."""
        self.assertEqual('UP', self.config.exit('U'))

    def test_get_poll(self):
        """Verify poll operations can be retrieved."""
        self.assertEqual(([], '[ $( date "+%H" ) = 0 ]', 'Q', 1800), self.config.get_poll('N'))

    def test_get_poll_with_branches(self):
        """Verify poll operations can be retrieved with branches."""
        self.assertEqual((['master', 'develop', 'release-1.0'], '', 'Q', 0),
                         self.config.get_poll('C', all_branches=['release-1.0']))

    def test_get_build(self):
        """Verify build operations can be retrieved."""
        self.assertEqual(('test_path', 'test'), self.config.get_build('T'))


if __name__ == '__main__':
    unittest.main()
