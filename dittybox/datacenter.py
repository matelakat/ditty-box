import abc


class Controller(object):
    def __init__(self, vm_name):
        self.vm_name = vm_name


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

    def install_vm(self, vm_name):
        validation_error = self._validate_install_vm(vm_name)
        if validation_error:
            return validation_error
        return Success(None)
