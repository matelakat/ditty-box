import unittest

from dittybox import script_provider
from dittybox import filesystem


class TestInstallScriptProvider(unittest.TestCase):
    def test_generate_setup_script(self):
        fs = filesystem.FakeFilesystem()

        fs.content_by_path['/path/to/setup/script'] = 'setupscript'

        prov = script_provider.PlainFileInstallScriptProvider(
            fs, '/path/to/setup/script')

        self.assertEquals('setupscript', prov.generate_install_script())


class TestPlainProvider(unittest.TestCase):
    def test_generate_upstart_script(self):
        prov = script_provider.PlainFileProvider(None, None)

        upstart_script = prov.generate_upstart_stream()
        self.assertTrue('start on runlevel' in upstart_script.read())

    def test_generate_onetime_script(self):
        fs = filesystem.FakeFilesystem()
        fs.content_by_path['/path/to/onetime/script'] = 'onetimescript'

        prov = script_provider.PlainFileProvider(
            fs, '/path/to/onetime/script')

        self.assertEquals(
            'onetimescript', prov.generate_onetime_stream().read())

