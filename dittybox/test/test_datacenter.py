import unittest

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

    def test_no_vm_found(self):
        result = self.dc.install_vm('vm1')

        self.assertTrue(result.failed)
        self.assertEquals("no such vm", result.data)

    def test_vm_found_but_no_controller_found(self):
        self.server.fake.add_vm('vm1')
        self.dc.controller = datacenter.Controller('controller')

        result = self.dc.install_vm('vm1')

        self.assertTrue(result.failed)
        self.assertEquals("controller vm not found", result.data)

    def test_install_controller_fails(self):
        self.server.fake.add_vm('controller')
        self.dc.controller = datacenter.Controller('controller')

        result = self.dc.install_vm('controller')

        self.assertTrue(result.failed)
        self.assertEquals('cannot install controller', result.data)

    def test_vm_and_controller_found(self):
        self.server.fake.add_vm('vm1')
        self.server.fake.add_vm('controller')
        self.dc.controller = datacenter.Controller('controller')

        result = self.dc.install_vm('vm1')

        self.assertFalse(result.failed)
