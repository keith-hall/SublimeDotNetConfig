# To run these tests, you will need to install
# https://packagecontrol.io/packages/UnitTesting
# and then use the `UnitTesting: Test Current File` entry in the command palette

import unittest
from SublimeDotNetConfig.build import find_base_file, is_base_file

class TestFindBaseFile(unittest.TestCase):
    def test_web_rc(self):
        self.assertEqual(find_base_file('Web.Release Candidate.config'), 'Web.config')

    def test_app(self): # TODO: make it possible to test falling back to `App.config` if the file with the same name as the executable doesn't exist
        self.assertEqual(find_base_file('Example.Application.Name.exe.Some-Transformation.config'), 'Example.Application.Name.exe.config')

class TestIsBaseFile(unittest.TestCase):
    def test_web_rc(self):
        self.assertFalse(is_base_file('Web.Release Candidate.config'))

    def test_web(self):
        self.assertTrue(is_base_file('Web.config'))

    def test_appexe(self):
        self.assertTrue(is_base_file('Example.Application.Name.exe.config'))

    def test_appexe_transform(self):
        self.assertFalse(is_base_file('Example.Application.Name.exe.Some-Transformation.config'))

    def test_app(self):
        self.assertTrue(is_base_file('App.config'))
