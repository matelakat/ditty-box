import abc

_IMPL = None


class Server(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def vms(self):
        pass

    @abc.abstractmethod
    def disconnect(self):
        pass

    @abc.abstractmethod
    def create_vm(self, mem_megs, disk_megs, network, vm_name):
        pass

    @abc.abstractmethod
    def delete_vm(self, vm):
        pass

    def vm_by_name(self, name):
        for vm in self.vms:
            if vm.name == name:
                return vm

    @abc.abstractmethod
    def detach_disk(self, disk, vm):
        pass

    @abc.abstractmethod
    def attach_disk(self, disk, vm):
        pass

    @abc.abstractproperty
    def networks(self):
        pass


class VM(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def name(self):
        pass

    @abc.abstractproperty
    def disks(self):
        pass

    @abc.abstractproperty
    def powered_off(self):
        pass

    @abc.abstractmethod
    def power_on(self):
        pass

    @abc.abstractmethod
    def power_off(self):
        pass

    @abc.abstractproperty
    def snapshots(self):
        pass

    @abc.abstractmethod
    def create_snapshot(self, snapshot_name):
        pass

    @abc.abstractmethod
    def revert_to_snapshot(self, snapshot_name):
        pass

    @abc.abstractmethod
    def delete_snapshot(self, snapshot_name):
        pass




class Disk(object):
    __metaclass__ = abc.ABCMeta

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.the_same_disk_as(other)
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    @abc.abstractmethod
    def the_same_disk_as(self, other_disk):
        pass


def get_server(host, password):
    return _IMPL.get_server(host, password)


def set_hypervisor(impl):
    global _IMPL
    _IMPL = impl
