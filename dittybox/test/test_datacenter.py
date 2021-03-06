import unittest
import mock

from dittybox import datacenter
from dittybox import controller
from dittybox import fake_hypervisor
from dittybox import hypervisor
from dittybox import vm_param_generator


class VMListTest(unittest.TestCase):
    def setUp(self):
        hv = fake_hypervisor.FakeHypervisor()
        hypervisor.set_hypervisor(hv)
        self.server = hypervisor.get_server('user', 'pass')
        self.dc = datacenter.Datacenter(self.server, None, None)

    def test_server_listing(self):
        vms = self.dc.list_vms()

        self.assertEquals([], vms)

    def test_server_listing_includes_power_state(self):
        self.server.fake.add_vm('some_vm')

        vms = self.dc.list_vms()

        self.assertEquals([('some_vm', 'OFF')], vms)

    def test_server_listing_includes_power_state(self):
        self.server.fake.add_vm('some_vm').power_on()

        vms = self.dc.list_vms()

        self.assertEquals([('some_vm', 'NOT OFF')], vms)


class VMInstallValidationTest(unittest.TestCase):
    def setUp(self):
        hv = fake_hypervisor.FakeHypervisor()
        hypervisor.set_hypervisor(hv)
        self.server = hypervisor.get_server('user', 'pass')
        self.dc = datacenter.Datacenter(self.server, None, None)
        self.install_vm_result = object()

    def test_no_vm_found(self):
        result = self.dc._validate_install_vm('vm1')

        self.assertTrue(result.failed)
        self.assertEquals("no such vm", result.data)

    def test_vm_found_but_no_controller_found(self):
        self.server.fake.add_vm('vm1')
        self.dc.controller = controller.FakeController('controller')

        result = self.dc._validate_install_vm('vm1')

        self.assertTrue(result.failed)
        self.assertEquals("controller vm not found", result.data)

    def test_install_controller_fails(self):
        self.server.fake.add_vm('controller')
        self.dc.controller = controller.FakeController('controller')

        result = self.dc._validate_install_vm('controller')

        self.assertTrue(result.failed)
        self.assertEquals('cannot install controller', result.data)

    def test_controller_is_busy(self):
        self.server.fake.add_vm('vm1')
        self.server.fake.add_vm('controller').fake.add_disks('disk1', 'disk2')
        self.dc.controller = controller.FakeController('controller')

        result = self.dc._validate_install_vm('vm1')

        self.assertTrue(result.failed)
        self.assertEquals(
            'controller already has a second disk attached', result.data)

    def test_valid(self):
        guest = self.server.fake.add_vm('vm1')
        guest_disk, = guest.fake.add_disks('guest-disk')
        ctrl = self.server.fake.add_vm('controller')
        ctrl.fake.add_disks('disk1')
        self.dc.controller = controller.FakeController('controller')

        result = self.dc._validate_install_vm('vm1')

        self.assertFalse(result.failed)

        self.assertEquals(
            (ctrl, guest, guest_disk), result.data)


class VMInstallTest(unittest.TestCase):
    def setUp(self):
        self.fake_calls = []
        hv = fake_hypervisor.FakeHypervisor(self.fake_calls)
        hypervisor.set_hypervisor(hv)
        self.server = hypervisor.get_server('user', 'pass')
        self.dc = datacenter.Datacenter(self.server, None, None)
        self.dc.controller = controller.FakeController('controller', self.fake_calls)
        self.vm = self.server.fake.add_vm('vm1')
        self.guest_disk, = self.vm.fake.add_disks('guest-disk')
        self.controller_vm = self.server.fake.add_vm('controller')
        self.controller_vm.fake.add_disks('ctrl-disk')
        self.controller_vm.power_on()

    def test_vms_power_state_guest_is_off(self):
        result = self.dc._install_vm(self.controller_vm, self.vm, self.guest_disk)

        self.assertFalse(result.failed)

        self.assertEquals([
                (self.server.attach_disk, self.guest_disk, self.controller_vm),
                self.dc.controller.plug_disk,
                (self.dc.controller.install_to_disk, dict(vm_name=self.vm.name)),
                self.dc.controller.unplug_disk,
                (self.server.detach_disk, self.guest_disk, self.controller_vm),
            ], self.fake_calls)

    def test_vms_power_state_guest_initially_on(self):
        self.vm.power_on()

        result = self.dc._install_vm(self.controller_vm, self.vm, self.guest_disk)

        self.assertFalse(result.failed)

        self.assertEquals([
                self.vm.power_off,
                (self.server.attach_disk, self.guest_disk, self.controller_vm),
                self.dc.controller.plug_disk,
                (self.dc.controller.install_to_disk, dict(vm_name=self.vm.name)),
                self.dc.controller.unplug_disk,
                (self.server.detach_disk, self.guest_disk, self.controller_vm),
            ], self.fake_calls)


class TestTestCase(unittest.TestCase):
    def test_controller_calls(self):
        fake_calls = []
        hv = fake_hypervisor.FakeHypervisor(fake_calls)
        hypervisor.set_hypervisor(hv)
        server = hypervisor.get_server('user', 'pass')
        ctr = controller.FakeController('controller', fake_calls)

        guest = server.fake.add_vm('vm1')
        guest_disk, = guest.fake.add_disks('guest-disk')
        controller_vm = server.fake.add_vm('controller')
        controller_vm.fake.add_disks('ctrl-disk')
        controller_vm.power_on()

        def sleep(time):
            guest.power_off()

        dc = datacenter.Datacenter(server, ctr, None, sleep=sleep)

        dc._vm_test(controller_vm, guest, 'data_provider')

        self.assertTrue(
            ctr.mount_guest_disk in fake_calls)

        self.assertTrue(
            ctr.umount_guest_disk in fake_calls)

        self.assertTrue(
            (ctr.upload_data, 'data_provider') in fake_calls)


class TestVMCreate(unittest.TestCase):
    def test_create_vm(self):
        hv = fake_hypervisor.FakeServer()
        hv.fake.add_vm('vm1')

        name_generator = vm_param_generator.FakeNameGenerator()
        name_generator.fake_name = 'somevm'
        dc = datacenter.Datacenter(hv, None, name_generator)

        vm_name = dc.vm_create(128, 20000, 'some_net')

        self.assertEquals('somevm', vm_name)
        self.assertEquals([['vm1']], name_generator.vm_names)
