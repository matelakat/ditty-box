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


class TestAddMount(unittest.TestCase, ConfigMixIn):
    def test_success(self):
        config = self.get_config(
            config_root='/opt/config', nginx_config_bits='/opt/nginx')

        result = config.add_mount(nginx_configurator.Mount('something', 'location'))

        self.assertEquals([
            'write /opt/config/something /opt/nginx/location',
            'write /opt/nginx/location config-for location',
        ], config.filesystem_manipulator.executed_commands)

        self.assertTrue(result.succeeded)

    def test_degenerate_mount(self):
        config = self.get_config(
            config_root='/opt/config', nginx_config_bits='/opt/nginx')

        mount = nginx_configurator.Mount(None, 'ignore')

        result = config.add_mount(mount)

        self.assertFalse(result.succeeded)
        self.assertEquals('degenerate mount', result.message)

    def test_location_already_mounted(self):
        config = self.get_config(
            fs_contents={
                '/opt/nginx/location': 'something'
            },
            config_root='/opt/config', nginx_config_bits='/opt/nginx')

        result = config.add_mount(nginx_configurator.Mount('something', 'location'))

        self.assertFalse(result.succeeded)
        self.assertEquals('location already mounted', result.message)

    def test_exception_on_fs_operation(self):
        config = self.get_config(
            config_root='/opt/config', nginx_config_bits='/opt/nginx')

        config.filesystem_manipulator.raise_errors = {
            'write /opt/config/something /opt/nginx/location': Exception('msg')}

        result = config.add_mount(nginx_configurator.Mount('something', 'location'))

        self.assertFalse(result.succeeded)
        self.assertEquals('msg', result.message)


class TestListMountPoints(unittest.TestCase, ConfigMixIn):
    def test_empty_list(self):
        config = self.get_config()

        result = config.list_mounts()

        self.assertTrue(result.succeeded)
        self.assertEquals([], result.mounts)

    def test_shows_externals(self):
        config = self.get_config(fs_contents={
            '/nginx/location': 'some_config'
            },
            config_root='/config_root',
            nginx_config_bits='/nginx')

        result = config.list_mounts()

        self.assertTrue(result.succeeded)
        self.assertEquals(
            [nginx_configurator.Mount(None, 'location')], result.mounts)

    def test_shows_unmounted(self):
        config = self.get_config(fs_contents={
            '/config_root/resource': 'nonexisting_config',
            },
            config_root='/config_root',
            nginx_config_bits='/nginx')

        result = config.list_mounts()

        self.assertTrue(result.succeeded)
        self.assertEquals(
            [nginx_configurator.Mount('resource', None)], result.mounts)

    def test_shows_proper_mounts(self):
        config = self.get_config(fs_contents={
            '/config_root/resource': 'location',
            '/nginx/location': 'ignore_me',
            },
            config_root='/config_root',
            nginx_config_bits='/nginx')

        result = config.list_mounts()

        self.assertTrue(result.succeeded)
        self.assertEquals(
            [nginx_configurator.Mount('resource', 'location')], result.mounts)


class TestDeleteMount(unittest.TestCase, ConfigMixIn):
    def test_delete_degenerate_mount(self):
        config = self.get_config()

        result = config.delete_mount(nginx_configurator.Mount(None, 'ignore'))

        self.assertFalse(result.succeeded)
        self.assertEquals('degenerate mount', result.message)

    def test_delete_mount(self):
        config = self.get_config(fs_contents={
            '/config_root/resource': 'location',
            '/nginx/location': 'ignore_me',
            },
            config_root='/config_root',
            nginx_config_bits='/nginx'
        )

        result = config.delete_mount(nginx_configurator.Mount('resource', 'location'))
        self.assertTrue(result.succeeded)

    def test_delete_mount_removes_entries(self):
        config = self.get_config(fs_contents={
            '/config_root/resource': 'location',
            '/nginx/location': 'ignore_me',
            },
            config_root='/config_root',
            nginx_config_bits='/nginx'
        )

        config.delete_mount(nginx_configurator.Mount('resource', 'location'))

        self.assertEquals([
            'rm /nginx/location',
            'rm /config_root/resource',
        ], config.filesystem_manipulator.executed_commands)

    def test_delete_non_existing_mount(self):
        config = self.get_config(fs_contents={},
            config_root='/config_root',
            nginx_config_bits='/nginx'
        )

        result = config.delete_mount(nginx_configurator.Mount('resource', 'location'))

        self.assertFalse(result.succeeded)
        self.assertEquals('non existing mount', result.message)
