import sys
import argparse
import importlib

from dittybox import hypervisor


def exercise_hypervisor(args):
    hypervisor_driver = importlib.import_module(args.driver)
    hypervisor.set_hypervisor(hypervisor_driver)
    hv = hypervisor.get_server(args.ip, args.password)

    networks = list(hv.networks)

    if len(networks) == 0:
        print "Failed to get networks"
        return 1

    network = networks[0]

    vm_list = list(hv.vms)

    vm = hv.create_vm(128, 20, network)

    vm_list_with_new_vm = list(hv.vms)

    if len(vm_list_with_new_vm) != len(vm_list) + 1:
        print "No vm created. Current vms: %s" % vm_list_with_new_vm
        return 1

    if args.interactive:
        print "VM created, press Enter to remove it"
        sys.stdin.readline()

    hv.delete_vm(vm)

    vm_list_after_vm_delete = list(hv.vms)

    if len(vm_list_after_vm_delete) != len(vm_list):
        print "vm not removed created. Current vms: %s" % vm_list_after_vm_delete
        return 1


    return 0


def main():
    parser = argparse.ArgumentParser(description='Test the hypervisor')
    parser.add_argument('driver', help='driver to use')
    parser.add_argument('ip', help='ip address of hypervisor')
    parser.add_argument('password', help='password for hypervisor')
    parser.add_argument('--interactive', help='interactive run', action='store_true')
    args = parser.parse_args()
    result = exercise_hypervisor(args)
    sys.exit(result)
