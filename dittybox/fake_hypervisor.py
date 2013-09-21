import mock

from dittybox import hypervisor


class FakeVM(hypervisor.VM):
    def __init__(self, name):
        self._name = name
        self._powered_off = True

    @property
    def disks(self):
        raise NotImplementedError()

    @property
    def name(self):
        return self._name

    def power_off(self):
        raise NotImplementedError()

    def power_on(self):
        if self.powered_off:
            self._powered_off = False
        else:
            raise AssertionError("Attempt to power on a non stopped vm")

    @property
    def powered_off(self):
        return self._powered_off


class TestMethodsMixIn(object):
    def __init__(self):
        self._vms = []

    def add_vm(self, vm_name):
        vm = FakeVM(vm_name)
        self._vms.append(vm)
        return vm


class FakeServer(hypervisor.Server, TestMethodsMixIn):
    @property
    def vms(self):
        return self._vms

    def attach_disk(self, disk, vm):
        raise NotImplementedError()

    def detach_disk(self, disk, vm):
        raise NotImplementedError()

    def disconnect(self):
        raise NotImplementedError()


class FakeHypervisor(object):
    def get_server(self, username, password):
        return FakeServer()
