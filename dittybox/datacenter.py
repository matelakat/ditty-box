import abc
import time
import textwrap


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
    def __init__(self, hypervisor, controller, name_generator, sleep=None):
        self.hypervisor = hypervisor
        self.controller = controller
        self.name_generator = name_generator
        self.sleep = sleep or time.sleep

    def vm_delete(self, vm_name):
        for vm in self.hypervisor.vms:
            if vm.name == vm_name:
                self.hypervisor.delete_vm(vm)

    def vm_create(self, mem_megs, disk_megs, network):
        vm_names = [vm.name for vm in self.hypervisor.vms]
        vm_name = self.name_generator.new_name(vm_names)
        vm = self.hypervisor.create_vm(mem_megs, disk_megs, network, vm_name)
        return vm.name

    def list_networks(self):
        return list(self.hypervisor.networks)

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

    def vm_create_snapshot(self, vm_name, snapshot_name):
        for vm in self.hypervisor.vms:
            if vm.name == vm_name:
                vm.create_snapshot(snapshot_name)
                return "Snapshot created"
        return "VM not found"

    def vm_delete_snapshot(self, vm_name, snapshot_name):
        for vm in self.hypervisor.vms:
            if vm.name == vm_name:
                vm.delete_snapshot(snapshot_name)
                return "Snapshot deleted"
        return "VM not found"

    def vm_revert_snapshot(self, vm_name, snapshot_name):
        for vm in self.hypervisor.vms:
            if vm.name == vm_name:
                vm.revert_to_snapshot(snapshot_name)
                return "Snapshot reverted"
        return "VM not found"

    def vm_list_snapshots(self, vm_name):
        for vm in self.hypervisor.vms:
            if vm.name == vm_name:
                return list(vm.snapshots)

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
        install_result = self.controller.install_to_disk(
            dict(vm_name=vm_to_install.name)
        )
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

    def _vm_test(self, vm_controller, vm_to_test, data_provider):
        if not vm_to_test.powered_off:
            vm_to_test.power_off()

        for snapshot_name in vm_to_test.snapshots:
            if snapshot_name == 'test':
                vm_to_test.revert_to_snapshot('test')
                break
        else:
            vm_to_test.create_snapshot('test')

        guest_disk, = vm_to_test.disks

        self.hypervisor.attach_disk(guest_disk, vm_controller)
        self.controller.plug_disk()
        self.controller.mount_guest_disk()
        self.controller.inject_onetime_script()
        self.controller.upload_data(data_provider)
        self.controller.umount_guest_disk()
        self.controller.unplug_disk()
        self.hypervisor.detach_disk(guest_disk, vm_controller)
        vm_to_test.power_on()

        while not vm_to_test.powered_off:
            self.sleep(1)

        self.hypervisor.attach_disk(guest_disk, vm_controller)
        self.controller.plug_disk()
        with open('soak_up.sh', 'rb') as soak_up_file:
            soak_up_result = self.controller.run_script(soak_up_file.read())
        self.controller.unplug_disk()
        self.hypervisor.detach_disk(guest_disk, vm_controller)
        vm_to_test.power_on()

        message = textwrap.dedent('''
        = Soak up =
        Standard output:
        %s
        Standard error:
        %s
        Return code:%s
        ''') % (
            soak_up_result.stdout,
            soak_up_result.stderr,
            soak_up_result.return_code)

        return Success(message)

    def vm_test(self, vm_name, data_provider):
        validation_result = self._validate_install_vm(vm_name)
        if validation_result.failed:
            return validation_result

        vm_controller, vm_to_test, _ignored = validation_result.data
        return self._vm_test(vm_controller, vm_to_test, data_provider)
