from pysphere import VIServer, VITask, VIProperty
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
    def __init__(self, name, esxi_server):
        self._name = name
        self.esxi_server = esxi_server

    @property
    def esxi_vm(self):
        return self.esxi_server.get_vm_by_name(self.name)

    @property
    def name(self):
        return self._name

    @property
    def esxi_power_state(self):
        props = self.esxi_server._retrieve_properties_traversal(
            property_names=['config.name', 'runtime.powerState'],
            obj_type="VirtualMachine")

        for prop_set in props:
            name = prop_set.PropSet[0].Val
            if name == self._name:
                return prop_set.PropSet[1].Val

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

    @property
    def snapshots(self):
        for snapshot in self.esxi_vm.get_snapshots():
            yield snapshot.get_name()

    def create_snapshot(self, snapshot_name):
        self.esxi_vm.create_snapshot(snapshot_name)

    def revert_to_snapshot(self, snapshot_name):
        self.esxi_vm.revert_to_named_snapshot(snapshot_name)

    def delete_snapshot(self, snapshot_name):
        self.esxi_vm.delete_named_snapshot(snapshot_name)


class ESXiServer(hypervisor.Server):
    def __init__(self, esxi_server):
        self.esxi_server = esxi_server

    @property
    def vms(self):
        props = self.esxi_server._retrieve_properties_traversal(
            property_names=['config.name'],
            obj_type="VirtualMachine")

        for prop_set in props or []:
            name = prop_set.PropSet[0].Val
            yield ESXiVM(name, self.esxi_server)

    def delete_vm(self, vm):
        #Invoke Destroy_Task
        request = VI.Destroy_TaskRequestMsg()

        _this = request.new__this(vm.esxi_vm._mor)
        _this.set_attribute_type(vm.esxi_vm._mor.get_attribute_type())
        request.set_element__this(_this)
        ret = self.esxi_server._proxy.Destroy_Task(request)._returnval
        task = VITask(ret, self.esxi_server)

        #Wait for the task to finish
        status = task.wait_for_state([task.STATE_SUCCESS, task.STATE_ERROR])
        if status == task.STATE_ERROR:
            raise VIException("Error removing vm:", task.get_error_message())

    def _create_vm_name(self):
        vm_names = [vm.name for vm in self.vms]

        counter = 0

        while True:
            vm_name = 'vm-%s' % counter
            if vm_name not in vm_names:
                return vm_name
            counter += 1

    def create_vm(self, mem_megs, disk_megs):
        vm_name = self._create_vm_name()

        datacenter = self._get_datacenter()
        datacenter_properties = self._get_datacenter_properties(datacenter)
        compute_resources = self._get_compute_resurces(datacenter)
        host = self._get_host()
        hostname = "ha-host"
        crprops = self._get_compute_properties(compute_resources, hostname)
        resource_pool = crprops.resourcePool._obj
        vm_folder = datacenter_properties.vmFolder._obj

        config_target = self._get_config_target(host, crprops)
        network_name = self._get_network_name(config_target)
        datastore_name = self.get_datastore_name(config_target)
        volume_name = "[%s]" % datastore_name

        self._create_vm(
            volume_name=volume_name,
            vm_name=vm_name,
            vm_description=vm_name,
            mem_megs=mem_megs,
            cpu_count=1,
            guest_os_id="rhel6Guest",
            disk_size=disk_megs * 1024,
            network_name=network_name,
            vm_folder=vm_folder,
            resource_pool=resource_pool,
            host=host)

        return ESXiVM(vm_name, self.esxi_server)

    def _create_vm(self, volume_name, vm_name, vm_description, mem_megs,
        cpu_count, guest_os_id, disk_size, network_name, vm_folder, resource_pool, host):

        create_vm_request = VI.CreateVM_TaskRequestMsg()
        config = create_vm_request.new_config()
        vmfiles = config.new_files()
        vmfiles.set_element_vmPathName(volume_name)
        config.set_element_files(vmfiles)
        config.set_element_name(vm_name)
        config.set_element_annotation(vm_description)
        config.set_element_memoryMB(mem_megs)
        config.set_element_numCPUs(cpu_count)
        config.set_element_guestId(guest_os_id)
        devices = []

        #add a scsi controller
        disk_ctrl_key = 1
        scsi_ctrl_spec =config.new_deviceChange()
        scsi_ctrl_spec.set_element_operation('add')
        scsi_ctrl = VI.ns0.VirtualLsiLogicController_Def("scsi_ctrl").pyclass()
        scsi_ctrl.set_element_busNumber(0)
        scsi_ctrl.set_element_key(disk_ctrl_key)
        scsi_ctrl.set_element_sharedBus("noSharing")

        scsi_ctrl_spec.set_element_device(scsi_ctrl)
        devices.append(scsi_ctrl_spec)

        # create a new disk - file based - for the vm
        disk_spec = config.new_deviceChange()
        disk_spec.set_element_fileOperation("create")
        disk_spec.set_element_operation("add")
        disk_ctlr = VI.ns0.VirtualDisk_Def("disk_ctlr").pyclass()
        disk_backing = VI.ns0.VirtualDiskFlatVer2BackingInfo_Def("disk_backing").pyclass()
        disk_backing.set_element_fileName(volume_name)
        disk_backing.set_element_diskMode("persistent")
        disk_ctlr.set_element_key(0)
        disk_ctlr.set_element_controllerKey(disk_ctrl_key)
        disk_ctlr.set_element_unitNumber(0)
        disk_ctlr.set_element_backing(disk_backing)
        disk_ctlr.set_element_capacityInKB(disk_size)
        disk_spec.set_element_device(disk_ctlr)
        devices.append(disk_spec)

        #add a NIC. the network Name must be set as the device name to create the NIC.
        nic_spec = config.new_deviceChange()
        nic_spec.set_element_operation("add")
        nic_ctlr = VI.ns0.VirtualPCNet32_Def("nic_ctlr").pyclass()
        nic_backing = VI.ns0.VirtualEthernetCardNetworkBackingInfo_Def("nic_backing").pyclass()
        nic_backing.set_element_deviceName(network_name)
        nic_ctlr.set_element_addressType("generated")
        nic_ctlr.set_element_backing(nic_backing)
        nic_ctlr.set_element_key(4)
        nic_spec.set_element_device(nic_ctlr)
        devices.append(nic_spec)

        config.set_element_deviceChange(devices)
        create_vm_request.set_element_config(config)
        folder_mor = create_vm_request.new__this(vm_folder)
        folder_mor.set_attribute_type(vm_folder.get_attribute_type())
        create_vm_request.set_element__this(folder_mor)
        rp_mor = create_vm_request.new_pool(resource_pool)
        rp_mor.set_attribute_type(resource_pool.get_attribute_type())
        create_vm_request.set_element_pool(rp_mor)
        host_mor = create_vm_request.new_host(host)
        host_mor.set_attribute_type(host.get_attribute_type())
        create_vm_request.set_element_host(host_mor)

        #CREATE THE VM
        taskmor = self.esxi_server._proxy.CreateVM_Task(create_vm_request)._returnval
        task = VITask(taskmor, self.esxi_server)
        task.wait_for_state([task.STATE_SUCCESS, task.STATE_ERROR])

        if task.get_state() == task.STATE_ERROR:
            raise Exception("Error creating vm: %s" %
        task.get_error_message())

    def get_datastore_name(self, config_target):
        for d in config_target.Datastore:
            if d.Datastore.Accessible:
                ds = d.Datastore.Datastore
                return d.Datastore.Name

    def _get_network_name(self, config_target):
        for n in config_target.Network:
            if n.Network.Accessible:
                    return n.Network.Name

    def _get_datacenter(self):
        datacentername = "ha-datacenter"
        dcmor = self.esxi_server._get_datacenters()[datacentername]
        return dcmor

    def _get_datacenter_properties(self, datacenter):
        return VIProperty(self.esxi_server, datacenter)

    def _get_host(self):
        for mor, name in self.esxi_server.get_hosts().items():
            if name == 'localhost.localdomain':
                return mor

    def _get_config_target(self, host, compute_properties):
        request = VI.QueryConfigTargetRequestMsg()
        _this = request.new__this(compute_properties.environmentBrowser._obj)
        _this.set_attribute_type(
            compute_properties.environmentBrowser._obj.get_attribute_type())
        request.set_element__this(_this)
        h = request.new_host(host)
        h.set_attribute_type(host.get_attribute_type())
        request.set_element_host(h)
        config_target = self.esxi_server._proxy.QueryConfigTarget(
            request)._returnval
        return config_target

    def _get_compute_resurces(self, datacenter):
        dcprops = VIProperty(self.esxi_server, datacenter)
        hfmor = dcprops.hostFolder._obj

        crmors = self.esxi_server._retrieve_properties_traversal(
            property_names=['name', 'host'],
            from_node=hfmor,
            obj_type='ComputeResource')
        return crmors

    def _get_compute_properties(self, compute_resources, hostname):
        crmor = None
        for cr in compute_resources:
            if crmor:
                break
            for p in cr.PropSet:
                if p.Name == "host":
                    for h in p.Val.get_element_ManagedObjectReference():
                        if h == hostname:
                            crmor = cr.Obj
                            break
                    if crmor:
                        break
        crprops = VIProperty(self.esxi_server, crmor)
        return crprops

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
