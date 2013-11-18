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

        cmd = main.create_cmd_interface('config_file', fs)

        self.assertEquals(
            'datacenter [config_file] >', cmd.prompt)

        self.assertEquals(
            'dittybox.esxi', cmd.dc.hypervisor.__class__.__module__)

        self.assertEquals(
            'hypervisor_ip', cmd.dc.hypervisor.host)

        self.assertEquals(
            'hypervisor_pass', cmd.dc.hypervisor.password)

        self.assertEquals(
            'controller_vm_name', cmd.dc.controller.vm_name)

        self.assertEquals(
            'controller_vm_ip', cmd.dc.controller.executor.host)

        self.assertEquals(
            'controller_vm_pass', cmd.dc.controller.executor.password)

        self.assertEquals(
            'controller_vm_ssh_config',
            cmd.dc.controller.executor.ssh_config)

        # TODO - this is ugly
        self.assertEquals(
            'data_file_path',
            cmd._config.data_provider.data_file)

        self.assertEquals(
            'install_script_path',
            cmd.dc.controller.install_script_provider.setup_script_path)

        # TODO - bad names are used here
        self.assertEquals(
            'test_script_path',
            cmd.dc.controller.setup_script_provider.onetime_script_path)
