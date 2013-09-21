import mock

from dittybox import hypervisor


class FakeDisk(hypervisor.Disk):
    def __init__(self, fake_name):
        self.fake_name = fake_name

    def the_same_disk_as(self, other_disk):
        return self.fake_name == other_disk.fake_name


class FakeVMMethods(object):
    def __init__(self):
        self.disks = []

    def add_disks(self, *disk_names):
        for disk_name in disk_names:
            self.disks.append(FakeDisk(disk_name))


class FakeVM(hypervisor.VM):
    def __init__(self, name):
        self._name = name
        self._powered_off = True
        self.fake = FakeVMMethods()

    @property
    def disks(self):
        return self.fake.disks

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


class FakeServerMethods(object):
    def __init__(self):
        self.vms = []

    def add_vm(self, vm_name):
        vm = FakeVM(vm_name)
        self.vms.append(vm)
        return vm


class FakeServer(hypervisor.Server):

    def __init__(self):
        self.fake = FakeServerMethods()

    @property
    def vms(self):
        return self.fake.vms

    def attach_disk(self, disk, vm):
        raise NotImplementedError()

    def detach_disk(self, disk, vm):
        raise NotImplementedError()

    def disconnect(self):
        raise NotImplementedError()


class FakeHypervisor(object):
    def get_server(self, username, password):
        return FakeServer()
