import mock

from dittybox import hypervisor


class FakeDisk(hypervisor.Disk):
    def __init__(self, fake_name):
        self.fake_name = fake_name

    def the_same_disk_as(self, other_disk):
        return self.fake_name == other_disk.fake_name


class FakeVMMethods(object):
    def __init__(self, fake_call_collector):
        self.disks = []
        if fake_call_collector is None:
            fake_call_collector = []
        self.call_collector = fake_call_collector

    def add_disks(self, *disk_names):
        result = []
        for disk_name in disk_names:
            disk = FakeDisk(disk_name)
            self.disks.append(disk)
            result.append(disk)
        return result


class FakeVM(hypervisor.VM):
    def __init__(self, name, fake_call_collector):
        self._name = name
        self._powered_off = True
        self.fake = FakeVMMethods(fake_call_collector)
        self.fake_snapshots = []

    @property
    def disks(self):
        return self.fake.disks

    @property
    def name(self):
        return self._name

    def power_off(self):
        if self.powered_off:
            raise AssertionError("Attempt to power off a stopped vm")
        self._powered_off = True
        self.fake.call_collector.append(self.power_off)

    def power_on(self):
        if self.powered_off:
            self._powered_off = False
        else:
            raise AssertionError("Attempt to power on a non stopped vm")

    @property
    def powered_off(self):
        return self._powered_off

    @property
    def snapshots(self):
        return self.fake_snapshots

    def create_snapshot(self, snapshot_name):
        self.fake_snapshots.append(snapshot_name)

    def revert_to_snapshot(self, snapshot_name):
        raise NotImplementedError()

    def delete_snapshot(self, snapshot_name):
        raise NotImplementedError()


class FakeServerMethods(object):
    def __init__(self, fake_call_collector):
        if fake_call_collector is None:
            fake_call_collector = []
        self.call_collector = fake_call_collector
        self.vms = []

    def add_vm(self, vm_name):
        vm = FakeVM(vm_name, self.call_collector)
        self.vms.append(vm)
        return vm


class FakeServer(hypervisor.Server):

    def __init__(self, fake_call_collector=None):
        if fake_call_collector is None:
            fake_call_collector = []
        self.fake_call_collector = fake_call_collector
        self.fake = FakeServerMethods(fake_call_collector)

    @property
    def vms(self):
        return self.fake.vms

    def attach_disk(self, disk, vm):
        self.fake_call_collector.append((self.attach_disk, disk, vm))

    def detach_disk(self, disk, vm):
        self.fake_call_collector.append((self.detach_disk, disk, vm))

    def disconnect(self):
        raise NotImplementedError()

    def create_vm(self, mem_megs, disk_megs, network, vm_name):
        return self.fake.add_vm(vm_name)

    def delete_vm(self, vm):
        raise NotImplementedError()

    @property
    def networks(self):
        raise NotImplementedError()


class FakeHypervisor(object):
    def __init__(self, fake_call_collector=None):
        if fake_call_collector is None:
            fake_call_collector = []
        self.fake_call_collector = fake_call_collector

    def get_server(self, username, password):
        return FakeServer(self.fake_call_collector)
