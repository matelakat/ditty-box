import unittest

from dittybox import controller
from dittybox import setup_scripts


class TestShellController(unittest.TestCase):
    def test_vm_name(self):
        ctrl = controller.ShellController('vmname', None, None)
        self.assertEquals('vmname', ctrl.vm_name)

    def test_unplug_disk(self):
        fake_exec = controller.FakeExecutor()
        ctrl = controller.ShellController('vm', fake_exec, None)

        ctrl.unplug_disk()

        self.assertEquals(
            ['echo "1" > /sys/block/sdb/device/delete'],
            fake_exec.fake_executed_commands)

    def test_plug_disk(self):
        fake_exec = controller.FakeExecutor()
        ctrl = controller.ShellController('vm', fake_exec, None)

        ctrl.plug_disk()

        self.assertEquals(
            ['echo "- - -" > /sys/class/scsi_host/host2/scan'],
            fake_exec.fake_executed_commands)

    def test_debootstrap_to_disk(self):
        fake_exec = controller.FakeExecutor()
        setup_script_provider = setup_scripts.FakeSetupScriptProvider()
        setup_script_provider.fake_setup_script = 'script'
        ctrl = controller.ShellController(
            'vm', fake_exec, setup_script_provider)

        ctrl.install_to_disk()

        self.assertEquals(['script'], fake_exec.fake_executed_scripts)
