import argparse
import cmd
import importlib


from dittybox import config
from dittybox import hypervisor
from dittybox import datacenter
from dittybox import controller
from dittybox import setup_scripts


class DatacenterCommands(cmd.Cmd):
    def do_exit(self, arg):
        return True

    def do_vm_list(self, arg):
        for vm_name, pwr in self.dc.list_vms():
            print vm_name, pwr

    def do_vm_install(self, arg):
        result = self.dc.install_vm(arg)
        if result.failed:
            print "FAIL", result.data
        else:
            print "SUCCESS", result.data

    def do_check_controller(self, arg):
        self.dc.controller.check()

    def do_show_install_script(self, arg):
        print self.dc.controller.setup_script_provider.generate_setup_script()


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

    executor = controller.SSHExecutor(cfg.controller)
    ctr = controller.ShellController(
        cfg.controller.vm_name,
        executor,
        setup_scripts.NullScriptProvider()
        )

    cmd_.dc = datacenter.Datacenter(hv, ctr)
    cmd_.cmdloop()
    hv.disconnect()
    executor.disconnect()
