import argparse
import cmd
import importlib


from dittybox import config
from dittybox import hypervisor


class DatacenterCommands(cmd.Cmd):
    def do_exit(self, arg):
        return True

    def do_vm_list(self, arg):
        for vm in self.hypervisor.vms:
            status = ' OFF' if vm.powered_off else ''
            print "%s%s" % (vm.name, status)

    def do_vm_install(self, arg):
        pass


def main():
    parser = argparse.ArgumentParser(description='Datacenter shell')
    parser.add_argument('config', help='Configuration file')
    args = parser.parse_args()

    with open(args.config, 'rb') as cfgfile:
        cfg = config.Configuration(cfgfile)

    cmd_ = DatacenterCommands()
    cmd_.prompt = "datacenter [%s] >" % args.config

    hypervisor_driver = importlib.import_module(cfg.hypervisor.driver)
    hypervisor.set_hypervisor(hypervisor_driver)

    cmd_.hypervisor = hypervisor.get_server(
        cfg.hypervisor.ip, cfg.hypervisor.password)
    cmd_.cmdloop()
    cmd_.hypervisor.disconnect()

