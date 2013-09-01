import argparse
from pysphere import VIServer, VITask
from pysphere.resources import VimService_services as VI


def get_server(host, password):
    server = VIServer()
    server.connect(host, "root", password)
    return server


def reconfig_request(vm):
    request = VI.ReconfigVM_TaskRequestMsg()
    _this = request.new__this(vm._mor)
    _this.set_attribute_type(vm._mor.get_attribute_type())
    request.set_element__this(_this)
    return request


def perform_reconfig(server, request):
    ret = server._proxy.ReconfigVM_Task(request)._returnval
    task = VITask(ret, server)
    status = task.wait_for_state([task.STATE_SUCCESS, task.STATE_ERROR])
    if status == task.STATE_SUCCESS:
        print "VM successfully reconfigured"
    elif status == task.STATE_ERROR:
        print "Error reconfiguring vm: %s" % task.get_error_message()


def get_disks(vm):
    disks = []
    for device in vm.properties.config.hardware.device:
        if device._type == "VirtualDisk":
            disks.append(device)
    return disks


def get_disk_path(disk):
    return disk.backing.fileName


def detach_disk(disk_path, vm, server):
    print "Detaching", disk_path, "from", vm.properties.name

    for disk in get_disks(vm):
        if disk_path == get_disk_path(disk):
            request = reconfig_request(vm)
            spec = request.new_spec()

            dc = spec.new_deviceChange()
            dc.Operation = "remove"
            dc.Device = disk._obj

            spec.DeviceChange = [dc]

            request.Spec = spec
            perform_reconfig(server, request)


def attach_disk(new_disk, vm, server):
    print "Attaching", get_disk_path(new_disk), "to", vm.properties.name

    unit_numbers = set()
    controllers = set()
    for disk in get_disks(vm):
        unit_numbers.add(disk.unitNumber)
        controllers.add(disk.controllerKey)

    new_unit_number = max(unit_numbers) + 1
    controller, = controllers

    assert new_disk.backing._type == "VirtualDiskFlatVer2BackingInfo"

    # Create backing
    backing = VI.ns0.VirtualDiskFlatVer2BackingInfo_Def("backing").pyclass()
    backing.FileName = new_disk.backing.fileName
    backing.DiskMode = new_disk.backing.diskMode
    backing.ThinProvisioned = new_disk.backing.thinProvisioned

    # Create HD
    hd = VI.ns0.VirtualDisk_Def("hd").pyclass()
    hd.Key = -100
    hd.CapacityInKB = new_disk.capacityInKB
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
    request = reconfig_request(vm)
    spec = request.new_spec()

    # Device change
    dc = spec.new_deviceChange()
    dc.Operation = "add"
    dc.Device = hd

    spec.DeviceChange = [dc]

    request.Spec = spec
    perform_reconfig(server, request)


def main(args):
    server = get_server(args.host, args.password)

    guest = server.get_vm_by_name(args.guest)
    controller = server.get_vm_by_name(args.controller)

    guest_disks = get_disks(guest)

    guest_disk, = guest_disks

    controller_disks = get_disks(controller)

    if get_disk_path(guest_disk) in [get_disk_path(d) for d in controller_disks]:
        detach_disk(get_disk_path(guest_disk), controller, server)
        if args.power:
            guest.power_on()
    else:
        if args.power:
            if guest.get_status() != 'POWERED OFF':
                guest.power_off()
        attach_disk(guest_disk, controller, server)

    server.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Toggle a virtual disk')
    parser.add_argument('host', help='ESXi host')
    parser.add_argument('password', help='Password for root')
    parser.add_argument('guest', help='Name of guest VM')
    parser.add_argument('controller', help='Name of controller VM')
    parser.add_argument('--power', help='Power on/off the VM',
                        action='store_true', default=False)
    args = parser.parse_args()
    main(args)
