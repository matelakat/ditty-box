import argparse
from pysphere import VIServer


def get_server(host, password):
    server = VIServer()
    server.connect(host, "root", password)
    return server


def get_args_for_list_vms():
    parser = argparse.ArgumentParser(description='List virtual machines')
    parser.add_argument('host', help='ESXi host')
    parser.add_argument('password', help='Password for root')
    return parser.parse_args()


def list_vms():
    args = get_args_for_list_vms()
    server = get_server(args.host, args.password)

    for vmpath in server.get_registered_vms():
        vm = server.get_vm_by_path(vmpath)
        print vm.properties.name, vm.get_status()

    server.disconnect()
