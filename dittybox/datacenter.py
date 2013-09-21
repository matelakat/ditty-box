import abc


class Controller(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def unplug_disk(self):
        pass

    @abc.abstractmethod
    def plug_disk(self):
        pass

    @abc.abstractmethod
    def debootstrap_to_disk(self):
        pass

    @abc.abstractproperty
    def vm_name(self):
        pass


class FakeController(Controller):
    def __init__(self, vm_name, fake_call_collector=None):
        self._vm_name = vm_name
        if fake_call_collector is None:
            fake_call_collector = []
        self.fake_call_collector = fake_call_collector

    @property
    def vm_name(self):
        return self._vm_name

    def plug_disk(self):
        self.fake_call_collector.append(self.plug_disk)

    def unplug_disk(self):
        self.fake_call_collector.append(self.unplug_disk)

    def debootstrap_to_disk(self):
        self.fake_call_collector.append(self.debootstrap_to_disk)


class Result(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def failed(self):
        pass

    @abc.abstractproperty
    def data(self):
        pass


class Success(Result):
    def __init__(self, data):
        self._data = data

    @property
    def failed(self):
        return False

    @property
    def data(self):
        return self._data


class Fail(Result):
    def __init__(self, message):
        self.message = message

    @property
    def failed(self):
        return True

    @property
    def data(self):
        return self.message


class Datacenter(object):
    def __init__(self, hypervisor, controller=None):
        self.hypervisor = hypervisor
        self.controller = controller

    def list_vms(self):
        result = []
        for vm in self.hypervisor.vms:
            result.append((vm.name, 'OFF' if vm.powered_off else 'NOT OFF'))
        return result

    def _validate_install_vm(self, vm_name):
        vm_to_install = None
        vm_controller = None

        for vm in self.hypervisor.vms:
            if vm.name == vm_name:
                vm_to_install = vm
            if vm.name == self.controller.vm_name:
                vm_controller = vm

        if vm_to_install is None:
            return Fail('no such vm')

        if vm_controller is None:
            return Fail('controller vm not found')

        if vm_to_install == vm_controller:
            return Fail('cannot install controller')

        if len(vm_controller.disks) != 1:
            return Fail('controller already has a second disk attached')

        guest_disk, = vm_to_install.disks

        return Success((vm_controller, vm_to_install, guest_disk))

    def _install_vm(self, vm_controller, vm_to_install, guest_disk):
        if not vm_to_install.powered_off:
            vm_to_install.power_off()

        self.hypervisor.attach_disk(guest_disk, vm_controller)
        self.controller.plug_disk()
        self.controller.debootstrap_to_disk()
        self.controller.unplug_disk()
        self.hypervisor.detach_disk(guest_disk, vm_controller)

        return Success(None)

    def install_vm(self, vm_name):
        validation_result = self._validate_install_vm(vm_name)
        if validation_result.failed:
            return validation_result
        return self._install_vm(*validation_result.data)
