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


class Disk(object):
    __metaclass__ = abc.ABCMeta


def get_server(host, password):
    return _IMPL.get_server(host, password)


def set_hypervisor(impl):
    global _IMPL
    _IMPL = impl
