import unittest

from dittybox.test import FakeStream

from dittybox import controller
from dittybox import script_provider
from dittybox import data_provider


class TestShellController(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_vm_name(self):
        ctrl = controller.ShellController('vmname', None, None)
        self.assertEquals('vmname', ctrl.vm_name)

    def test_unplug_disk(self):
        fake_exec = controller.FakeExecutor()
        ctrl = controller.ShellController('vm', fake_exec, None)

        ctrl.unplug_disk()

        self.assertEquals(
            [(fake_exec.sudo, 'echo "1" > /sys/block/sdb/device/delete')],
            fake_exec.fake_calls)

    def test_plug_disk(self):
        fake_exec = controller.FakeExecutor()
        ctrl = controller.ShellController('vm', fake_exec, None)

        ctrl.plug_disk()

        self.assertEquals([
            (fake_exec.sudo, 'echo "- - -" > /sys/class/scsi_host/host2/scan')
            ], fake_exec.fake_calls)

    def test_debootstrap_to_disk(self):
        fake_exec = controller.FakeExecutor()
        setup_script_provider = script_provider.FakeSetupScriptProvider()
        setup_script_provider.fake_setup_script = 'script'
        ctrl = controller.ShellController(
            'vm', fake_exec, setup_script_provider)

        ctrl.install_to_disk()

        self.assertEquals([
            (fake_exec.sudo_script, 'script')
            ], fake_exec.fake_calls)

    def test_mount_guest_disk_success(self):
        fake_exec = controller.FakeExecutor()

        ctrl = controller.ShellController('vm', fake_exec, None)
        ctrl.mount_guest_disk()

        self.assertEquals([
            (fake_exec.sudo, 'mkdir -p /mnt/ubuntu'),
            (fake_exec.sudo, 'mount /dev/sdb1 /mnt/ubuntu'),
            ],
            fake_exec.fake_calls)

    def test_umount_guest_disk_success(self):
        fake_exec = controller.FakeExecutor()

        ctrl = controller.ShellController('vm', fake_exec, None)
        ctrl.umount_guest_disk()

        self.assertEquals([
            (fake_exec.sudo, 'umount /dev/sdb1'),
            ],
            fake_exec.fake_calls)

    def test_umount_guest_disk_retries(self):
        fake_exec = controller.FakeExecutor()
        fake_exec.fake_sudo_failures = [(fake_exec.sudo, 'umount /dev/sdb1')] * 2

        ctrl = controller.ShellController('vm', fake_exec, None)
        ctrl.umount_guest_disk()

        self.assertEquals([
            (fake_exec.sudo, 'umount /dev/sdb1'),
            (fake_exec.wait,),
            (fake_exec.sudo, 'umount /dev/sdb1'),
            (fake_exec.wait,),
            (fake_exec.sudo, 'umount /dev/sdb1'),
            ],
            fake_exec.fake_calls)

    def test_inject_onetime_script(self):
        fake_exec = controller.FakeExecutor()
        setup_script_provider = script_provider.FakeSetupScriptProvider()
        setup_script_provider.fake_upstart_script = 'upstart_script'
        setup_script_provider.fake_onetime_script = 'somescript'

        ctrl = controller.ShellController('vm', fake_exec, setup_script_provider)
        ctrl.inject_onetime_script()

        self.assertEquals([
            (fake_exec.put, 'somescript', '/mnt/ubuntu/root/install.sh'),
            (fake_exec.put, 'upstart_script', '/mnt/ubuntu/etc/init/install.conf'),
            ],
            fake_exec.fake_calls)

    def test_upload_data_first_time(self):
        fake_exec = controller.FakeExecutor()
        fake_exec.fake_sudo_failures = [
            (fake_exec.sudo, 'test -f /datacenter_data/md5sum')]
        dp = data_provider.FakeDataProvider()
        dp.fake_md5sum = 'md5sum'
        dp.fake_stream = FakeStream()

        ctrl = controller.ShellController('vm', fake_exec, None)

        ctrl.upload_data(dp)

        self.assertEquals([
            (fake_exec.sudo, 'mkdir -p /datacenter_data'),
            (fake_exec.sudo, 'test -f /datacenter_data/md5sum'),
            (fake_exec.put, dp.fake_stream, '/datacenter_data/md5sum'),
            (fake_exec.sudo, 'cp /datacenter_data/md5sum /mnt/ubuntu/root/data.blob'),
            ],
            fake_exec.fake_calls)

        self.assertTrue(dp.fake_stream.closed)

    def test_upload_data_found_in_cache(self):
        fake_exec = controller.FakeExecutor()
        dp = data_provider.FakeDataProvider()
        dp.fake_md5sum = 'md5sum'

        ctrl = controller.ShellController('vm', fake_exec, None)

        ctrl.upload_data(dp)

        self.assertEquals([
            (fake_exec.sudo, 'mkdir -p /datacenter_data'),
            (fake_exec.sudo, 'test -f /datacenter_data/md5sum'),
            (fake_exec.sudo, 'cp /datacenter_data/md5sum /mnt/ubuntu/root/data.blob'),
            ],
            fake_exec.fake_calls)
