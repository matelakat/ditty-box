import unittest
import textwrap

from dittybox import main
from dittybox import filesystem


class TestMain(unittest.TestCase):
    def test_empty_config_file(self):
        fs = filesystem.FakeFilesystem()
        fs.content_by_path = {
            'config_file' : ''
        }

        with self.assertRaises(main.ConfigException) as ctx:
            result = main.create_cmd_interface('config_file', fs)

    def test_config_file_not_found(self):
        fs = filesystem.FakeFilesystem()
        fs.content_by_path = {}

        with self.assertRaises(main.ConfigException) as ctx:
            result = main.create_cmd_interface('config_file', fs)

        self.assertEquals(
            'Failed to read configuration file', ctx.exception.message)

    def test_proper_config_file(self):
        fs = filesystem.FakeFilesystem()
        fs.content_by_path = {
            'config_file': textwrap.dedent("""
            [hypervisor]
            driver = dittybox.esxi
            ip = hypervisor_ip
            password = hypervisor_pass

            [controller]
            vm_name = controller_vm_name
            host = controller_vm_ip
            password = controller_vm_pass
            ssh_config = controller_vm_ssh_config

            [data_provider]
            data_file = data_file_path

            [script_provider]
            install = install_script_path
            test = test_script_path
            """)
        }

        result = main.create_cmd_interface('config_file', fs)
