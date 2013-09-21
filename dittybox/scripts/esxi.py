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

    props = server._retrieve_properties_traversal(
        property_names=['config.name', 'runtime.powerState'],
        obj_type="VirtualMachine")

    for prop_set in props:
        print ' '.join(prop.Val for prop in prop_set.PropSet)

    server.disconnect()
