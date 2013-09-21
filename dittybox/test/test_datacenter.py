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
        self.server.test_methods.add_vm('some_vm')

        vms = self.dc.list_vms()

        self.assertEquals([('some_vm', 'OFF')], vms)

    def test_server_listing_includes_power_state(self):
        self.server.test_methods.add_vm('some_vm').power_on()

        vms = self.dc.list_vms()

        self.assertEquals([('some_vm', 'NOT OFF')], vms)
