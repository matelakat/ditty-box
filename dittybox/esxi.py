from pysphere import VIServer, VITask
from pysphere.resources import VimService_services as VI

from dittybox import hypervisor


class ESXiDisk(hypervisor.Disk):
    def __init__(self, esxi_disk):
        self.esxi_disk = esxi_disk

    def the_same_disk_as(self, other_disk):
        return self.esxi_filename == other_disk.esxi_filename

    @property
    def esxi_filename(self):
        return self.esxi_disk.backing.fileName


class ESXiVM(hypervisor.VM):
    def __init__(self, name, power_state, esxi_server):
        self._name = name
        self._power_state = power_state
        self.esxi_server = esxi_server
        self._vm = None

    @property
    def esxi_vm(self):
        if self._vm is None:
            self._vm = self.esxi_server.get_vm_by_name(self.name)
        return self._vm

    @property
    def name(self):
        return self._name

    @property
    def esxi_power_state(self):
        return self._power_state

    @property
    def disks(self):
        disks = []
        for device in self.esxi_vm.properties.config.hardware.device:
            if device._type == "VirtualDisk":
                disks.append(ESXiDisk(device))
        return disks

    def power_off(self):
        self.esxi_vm.power_off()

    def power_on(self):
        self.esxi_vm.power_on()

    @property
    def powered_off(self):
        return self.esxi_power_state == "poweredOff"


class ESXiServer(hypervisor.Server):
    def __init__(self, esxi_server):
        self.esxi_server = esxi_server

    @property
    def vms(self):
        props = self.esxi_server._retrieve_properties_traversal(
            property_names=['config.name', 'runtime.powerState'],
            obj_type="VirtualMachine")

        for prop_set in props:
            name = prop_set.PropSet[0].Val
            power_state = prop_set.PropSet[1].Val
            yield ESXiVM(name, power_state, self.esxi_server)

    def disconnect(self):
        self.esxi_server.disconnect()

    def detach_disk(self, disk, vm):
        for attached_disk in vm.disks:
            if attached_disk == disk:
                request = reconfig_request(vm.esxi_vm)
                spec = request.new_spec()

                dc = spec.new_deviceChange()
                dc.Operation = "remove"
                dc.Device = attached_disk.esxi_disk._obj

                spec.DeviceChange = [dc]

                request.Spec = spec
                self.perform_reconfig(request)
                return

        assert False, "The given disk is not attached to this vm"

    def attach_disk(self, disk, vm):
        new_esxi_disk = disk.esxi_disk

        unit_numbers = set()
        controllers = set()

        for esxi_disk in [disk.esxi_disk for disk in vm.disks]:
            unit_numbers.add(esxi_disk.unitNumber)
            controllers.add(esxi_disk.controllerKey)

        new_unit_number = max(unit_numbers) + 1
        controller, = controllers

        assert new_esxi_disk.backing._type == "VirtualDiskFlatVer2BackingInfo"

        # Create backing
        backing = VI.ns0.VirtualDiskFlatVer2BackingInfo_Def("backing").pyclass()
        backing.FileName = new_esxi_disk.backing.fileName
        backing.DiskMode = new_esxi_disk.backing.diskMode
        backing.ThinProvisioned = new_esxi_disk.backing.thinProvisioned

        # Create HD
        hd = VI.ns0.VirtualDisk_Def("hd").pyclass()
        hd.Key = -100
        hd.CapacityInKB = new_esxi_disk.capacityInKB
        hd.UnitNumber = new_unit_number
        hd.ControllerKey = controller
        hd.Backing = backing

        # Connectable
        connectable = hd.new_connectable()
        connectable.StartConnected = True
        connectable.AllowGuestControl = False
        connectable.Connected = True
        hd.Connectable = connectable

        # Configure
        request = reconfig_request(vm.esxi_vm)
        spec = request.new_spec()

        # Device change
        dc = spec.new_deviceChange()
        dc.Operation = "add"
        dc.Device = hd

        spec.DeviceChange = [dc]

        request.Spec = spec
        self.perform_reconfig(request)

    def perform_reconfig(self, request):
        ret = self.esxi_server._proxy.ReconfigVM_Task(request)._returnval
        task = VITask(ret, self.esxi_server)
        status = task.wait_for_state([task.STATE_SUCCESS, task.STATE_ERROR])
        if status == task.STATE_SUCCESS:
            print "VM successfully reconfigured"
        elif status == task.STATE_ERROR:
            print "Error reconfiguring vm: %s" % task.get_error_message()


def reconfig_request(esxi_vm):
    request = VI.ReconfigVM_TaskRequestMsg()
    _this = request.new__this(esxi_vm._mor)
    _this.set_attribute_type(esxi_vm._mor.get_attribute_type())
    request.set_element__this(_this)
    return request


def get_server(host, password):
    server = VIServer()
    server.connect(host, "root", password)
    return ESXiServer(server)
