import unittest
from dittybox import nginx_configurator
from dittybox import filesystem


class TestMountPointOf(unittest.TestCase):
    def get_config(self, fs_contents={}, config_root='', nginx_config_bits=''):
        fs = filesystem.FakeFilesystem()
        fs.content_by_path = fs_contents

        return nginx_configurator.create(fs, config_root, nginx_config_bits)

    def test_empty(self):
        configurator = self.get_config()

        self.assertEquals(None, configurator.mount_point_of('something'))

    def test_existing(self):
        configurator = self.get_config(
            config_root='/opt/resources',
            nginx_config_bits='/opt/nginx',
            fs_contents={
                '/opt/resources/something': '/opt/nginx/mountpoint',
                '/opt/nginx/mountpoint': 'ignore'
            }
        )

        self.assertEquals(
            'mountpoint', configurator.mount_point_of('something'))

    def test_target_not_existing(self):
        configurator = self.get_config(
            config_root='/opt/resources',
            nginx_config_bits='/opt/nginx',
            fs_contents={
                '/opt/resources/something': '/opt/nginx/mountpoint',
            }
        )

        self.assertEquals(
            None, configurator.mount_point_of('something'))
