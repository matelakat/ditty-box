import unittest
from dittybox import nginx_configurator
from dittybox import filesystem
from dittybox import filesystem_manipulator


class ConfigMixIn(object):
    def get_config(self, fs_contents={}, config_root='', nginx_config_bits=''):
        fs = filesystem.FakeFilesystem()
        fs.content_by_path = fs_contents

        return nginx_configurator.create(
            fs, filesystem_manipulator.Fake(), config_root, nginx_config_bits,
            nginx_configurator.fake_config_generator)


class TestMountPointOf(ConfigMixIn, unittest.TestCase):
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


class TestSetMountPoint(unittest.TestCase, ConfigMixIn):
    def test_setting_a_mountpoint(self):
        config = self.get_config(
            config_root='/opt/config', nginx_config_bits='/opt/nginx')

        result = config.set_mountpoint('something', 'location')

        self.assertEquals([
            'write /opt/config/something /opt/nginx/location',
            'write /opt/nginx/location config-for location',
        ], config.filesystem_manipulator.executed_commands)

        self.assertTrue(result.succeeded)

    def test_location_already_mounted(self):
        config = self.get_config(
            fs_contents={
                '/opt/nginx/location': 'something'
            },
            config_root='/opt/config', nginx_config_bits='/opt/nginx')

        result = config.set_mountpoint('something', 'location')

        self.assertFalse(result.succeeded)
        self.assertEquals('location already mounted', result.message)

    def test_exception_on_fs_operation(self):
        config = self.get_config(
            config_root='/opt/config', nginx_config_bits='/opt/nginx')

        config.filesystem_manipulator.raise_errors = {
            'write /opt/config/something /opt/nginx/location': Exception('msg')}

        result = config.set_mountpoint('something', 'location')

        self.assertFalse(result.succeeded)
        self.assertEquals('msg', result.message)


class TestListMountPoints(unittest.TestCase, ConfigMixIn):
    def test_empty_list(self):
        config = self.get_config()

        result = config.list_mounts()

        self.assertTrue(result.succeeded)
        self.assertEquals([], result.mounts)
