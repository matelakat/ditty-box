import argparse
import cmd
import importlib


from dittybox import config
from dittybox import hypervisor
from dittybox import datacenter


class DatacenterCommands(cmd.Cmd):
    def do_exit(self, arg):
        return True

    def do_vm_list(self, arg):
        for vm_name, pwr in self.dc.list_vms():
            print vm_name, pwr

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

    hv = hypervisor.get_server(cfg.hypervisor.ip, cfg.hypervisor.password)

    cmd_.dc = datacenter.Datacenter(hv)
    cmd_.cmdloop()
    hv.disconnect()
