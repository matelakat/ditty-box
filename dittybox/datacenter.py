import abc


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
    def __init__(self, hypervisor, controller):
        self.hypervisor = hypervisor
        self.controller = controller

    def list_vms(self):
        result = []
        for vm in self.hypervisor.vms:
            result.append((vm.name, 'OFF' if vm.powered_off else 'NOT OFF'))
        return result

    def vm_start(self, vm_name):
        for vm in self.hypervisor.vms:
            if vm.name == vm_name:
                vm.power_on()
                return "VM started"
        return "VM not found"

    def vm_stop(self, vm_name):
        for vm in self.hypervisor.vms:
            if vm.name == vm_name:
                vm.power_off()
                return "VM stopped"
        return "VM not found"

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
        install_result = self.controller.install_to_disk()
        self.controller.unplug_disk()
        self.hypervisor.detach_disk(guest_disk, vm_controller)

        message = 'Standard output:%s\nStandard error:%s\nReturn code:%s' % (
            install_result.stdout, install_result.stderr, install_result.return_code)
        return Success(message)

    def install_vm(self, vm_name):
        validation_result = self._validate_install_vm(vm_name)
        if validation_result.failed:
            return validation_result
        return self._install_vm(*validation_result.data)
