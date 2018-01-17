# To run these tests, you will need to install
# https://packagecontrol.io/packages/UnitTesting
# and then use the `UnitTesting: Test Current File` entry in the command palette

import unittest
from SublimeDotNetConfig.build import find_base_file

class TestFindBaseFile(unittest.TestCase):
    def test_web_rc(self):
        self.assertEqual(find_base_file('Web.Release Candidate.config'), 'Web.config')

    def test_app(self): # TODO: also allow falling back to `App.config` if the file with the same name as the executable doesn't exist
        self.assertEqual(find_base_file('Example.Application.Name.exe.config'), 'Example.Application.Name.config')
