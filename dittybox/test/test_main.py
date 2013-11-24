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

            [install_script_provider]
            cls = TemplateBasedInstallScriptProvider
            script_path = install_script_path

            [user_script_provider]
            script_path = user_script_path

            [name_generator]
            prefix = vm-
            first_id = 10
            last_id = 12
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

        self.assertEquals(
            'data_file_path',
            cmd.data_provider.data_path)

        self.assertEquals(
            'install_script_path',
            cmd.dc.controller.install_script_provider.script_path)

        self.assertEquals(
            'user_script_path',
            cmd.dc.controller.user_script_provider.script_path)

        self.assertEquals(
            'vm-',
            cmd.dc.name_generator.prefix)

        self.assertEquals(
            10,
            cmd.dc.name_generator.first_id)

        self.assertEquals(
            12,
            cmd.dc.name_generator.last_id)
