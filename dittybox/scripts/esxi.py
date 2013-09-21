import argparse

from dittybox import hypervisor


def get_args_for_list_vms():
    parser = argparse.ArgumentParser(description='List virtual machines')
    parser.add_argument('host', help='ESXi host')
    parser.add_argument('password', help='Password for root')
    return parser.parse_args()


def list_vms():
    args = get_args_for_list_vms()
    from dittybox import esxi
    hypervisor.set_hypervisor(esxi)

    server = hypervisor.get_server(args.host, args.password)

    for vm in server.vms:
        print vm.name, "OFF" if vm.powered_off else "ON"

    server.disconnect()


def get_args_for_toggle_disk():
    parser = argparse.ArgumentParser(description='Toggle a virtual disk')
    parser.add_argument('host', help='ESXi host')
    parser.add_argument('password', help='Password for root')
    parser.add_argument('guest', help='Name of guest VM')
    parser.add_argument('controller', help='Name of controller VM')
    parser.add_argument('--power', help='Power on/off the VM',
                        action='store_true', default=False)
    return parser.parse_args()


def toggle_disk():
    args = get_args_for_toggle_disk()
    from dittybox import esxi
    hypervisor.set_hypervisor(esxi)

    server = hypervisor.get_server(args.host, args.password)

    guest = server.vm_by_name(args.guest)
    controller = server.vm_by_name(args.controller)

    guest_disks = guest.disks

    guest_disk, = guest_disks

    controller_disks = controller.disks

    def attach_to_controller():
        print "Attaching disk to controller"
        if args.power:
            if not guest.powered_off:
                guest.power_off()
        server.attach_disk(guest_disk, controller)

    def detach_from_controller():
        print "Detaching disk from controller"
        server.detach_disk(guest_disk, controller)
        if args.power:
            guest.power_on()

    if guest_disk in controller_disks:
        operation = detach_from_controller
    else:
        operation = attach_to_controller

    operation()

    server.disconnect()
