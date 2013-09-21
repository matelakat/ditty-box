import unittest

from dittybox import datacenter
from dittybox import fake_hypervisor
from dittybox import hypervisor


class VMListTest(unittest.TestCase):
    def test_server_listing(self):
        hv = fake_hypervisor.FakeHypervisor()
        hypervisor.set_hypervisor(hv)
        server = hypervisor.get_server('user', 'pass')

        dc = datacenter.Datacenter(server)

        vms = dc.list_vms()
        self.assertEquals([], vms)

    def test_server_listing_includes_power_state(self):
        hv = fake_hypervisor.FakeHypervisor()
        hypervisor.set_hypervisor(hv)
        server = hypervisor.get_server('user', 'pass')
        server.test_methods.add_vm('some_vm')

        dc = datacenter.Datacenter(server)

        vms = dc.list_vms()
        self.assertEquals([('some_vm', 'OFF')], vms)

    def test_server_listing_includes_power_state(self):
        hv = fake_hypervisor.FakeHypervisor()
        hypervisor.set_hypervisor(hv)
        server = hypervisor.get_server('user', 'pass')
        server.test_methods.add_vm('some_vm').power_on()

        dc = datacenter.Datacenter(server)

        vms = dc.list_vms()
        self.assertEquals([('some_vm', 'NOT OFF')], vms)
