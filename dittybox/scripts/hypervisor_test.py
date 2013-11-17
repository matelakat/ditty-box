import sys
import argparse
import importlib

from dittybox import hypervisor


def exercise_hypervisor(args):
    hypervisor_driver = importlib.import_module(args.driver)
    hypervisor.set_hypervisor(hypervisor_driver)
    hv = hypervisor.get_server(args.ip, args.password)

    vm_list = list(hv.vms)

    vm = hv.create_vm(128, 20)

    vm_list_with_new_vm = list(hv.vms)

    if vm_list_with_new_vm == vm_list:
        print "No vm created. Current vms: %s" % vm_list_with_new_vm
        return 1

    hv.delete_vm(vm)

    vm_list_after_vm_delete = list(hv.vms)

    if vm_list_after_vm_delete != vm_list:
        print "vm not removed created. Current vms: %s" % vm_list_after_vm_delete
        return 1

    return 0


def main():
    parser = argparse.ArgumentParser(description='Test the hypervisor')
    parser.add_argument('driver', help='driver to use')
    parser.add_argument('ip', help='ip address of hypervisor')
    parser.add_argument('password', help='password for hypervisor')
    args = parser.parse_args()
    result = exercise_hypervisor(args)
    sys.exit(result)
