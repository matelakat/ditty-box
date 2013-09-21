import unittest
import mock

from dittybox import datacenter
from dittybox import fake_hypervisor
from dittybox import hypervisor


class VMListTest(unittest.TestCase):
    def setUp(self):
        hv = fake_hypervisor.FakeHypervisor()
        hypervisor.set_hypervisor(hv)
        self.server = hypervisor.get_server('user', 'pass')
        self.dc = datacenter.Datacenter(self.server)

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
        self.dc = datacenter.Datacenter(self.server)
        self.install_vm_result = object()

    def test_no_vm_found(self):
        result = self.dc._validate_install_vm('vm1')

        self.assertTrue(result.failed)
        self.assertEquals("no such vm", result.data)

    def test_vm_found_but_no_controller_found(self):
        self.server.fake.add_vm('vm1')
        self.dc.controller = datacenter.FakeController('controller')

        result = self.dc._validate_install_vm('vm1')

        self.assertTrue(result.failed)
        self.assertEquals("controller vm not found", result.data)

    def test_install_controller_fails(self):
        self.server.fake.add_vm('controller')
        self.dc.controller = datacenter.FakeController('controller')

        result = self.dc._validate_install_vm('controller')

        self.assertTrue(result.failed)
        self.assertEquals('cannot install controller', result.data)

    def test_controller_is_busy(self):
        self.server.fake.add_vm('vm1')
        self.server.fake.add_vm('controller').fake.add_disks('disk1', 'disk2')
        self.dc.controller = datacenter.FakeController('controller')

        result = self.dc._validate_install_vm('vm1')

        self.assertTrue(result.failed)
        self.assertEquals(
            'controller already has a second disk attached', result.data)

    def test_valid(self):
        guest = self.server.fake.add_vm('vm1')
        guest_disk, = guest.fake.add_disks('guest-disk')
        controller = self.server.fake.add_vm('controller')
        controller.fake.add_disks('disk1')
        self.dc.controller = datacenter.FakeController('controller')

        result = self.dc._validate_install_vm('vm1')

        self.assertFalse(result.failed)

        self.assertEquals(
            (controller, guest, guest_disk), result.data)


class VMInstallTest(unittest.TestCase):
    def setUp(self):
        self.fake_calls = []
        hv = fake_hypervisor.FakeHypervisor(self.fake_calls)
        hypervisor.set_hypervisor(hv)
        self.server = hypervisor.get_server('user', 'pass')
        self.dc = datacenter.Datacenter(self.server)
        self.dc.controller = datacenter.FakeController('controller', self.fake_calls)
        self.dc._validate_install_vm = mock.Mock(return_value=None)
        self.vm = self.server.fake.add_vm('vm1')
        self.guest_disk, = self.vm.fake.add_disks('guest-disk')
        self.controller_vm = self.server.fake.add_vm('controller')
        self.controller_vm.fake.add_disks('ctrl-disk')
        self.controller_vm.power_on()

    def test_vms_power_state_guest_is_off(self):
        result = self.dc._install_vm(self.controller_vm, self.vm, self.guest_disk)

        self.assertFalse(result.failed)

        self.assertTrue(self.vm.powered_off)
        self.assertFalse(self.controller_vm.powered_off)

    def test_vms_power_state_guest_initially_on(self):
        self.vm.power_on()

        result = self.dc._install_vm(self.controller_vm, self.vm, self.guest_disk)

        self.assertFalse(result.failed)

        self.assertTrue(self.vm.powered_off)
        self.assertFalse(self.controller_vm.powered_off)

        self.assertEquals([
                (self.server.attach_disk, self.guest_disk, self.controller_vm),
                self.dc.controller.plug_disk,
                self.dc.controller.debootstrap_to_disk,
                self.dc.controller.unplug_disk,
                (self.server.detach_disk, self.guest_disk, self.controller_vm),
            ], self.fake_calls)
