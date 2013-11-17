import sys
import argparse
import importlib

from dittybox import hypervisor


def exercise_hypervisor(args):
    hypervisor_driver = importlib.import_module(args.driver)
    hypervisor.set_hypervisor(hypervisor_driver)
    hv = hypervisor.get_server(args.ip, args.password)

    vms = list(hv.vms)

    hv.create_vm(128, 20)

    new_vms = list(hv.vms)

    if new_vms == vms:
        print "No vm created. Current vms: %s" % new_vms
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
