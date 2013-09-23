import argparse
import cmd
import importlib


from dittybox import config
from dittybox import hypervisor
from dittybox import datacenter
from dittybox import controller
from dittybox import script_provider


class DatacenterCommands(cmd.Cmd):
    def do_exit(self, arg):
        return True

    def do_vm_list(self, arg):
        for vm_name, pwr in self.dc.list_vms():
            print vm_name, pwr

    def do_vm_start(self, arg):
        self.dc.vm_start(arg)

    def do_vm_stop(self, arg):
        self.dc.vm_stop(arg)

    def do_vm_install(self, arg):
        result = self.dc.install_vm(arg)
        if result.failed:
            print "FAIL", result.data
        else:
            print "SUCCESS", result.data

    def do_vm_list_snapshots(self, arg):
        snapshots = self.dc.vm_list_snapshots(arg)
        if snapshots is None:
            print "VM not found"
        else:
            for snapshot_name in snapshots:
                print snapshot_name

    def _create_snapshot_args(self, arg):
        if len(arg.split()) != 2:
            print "Two arguments needed: vm_name snapshot_name"
            return None
        return tuple(arg.split())

    def do_vm_create_snapshot(self, arg):
        snapshot_args = self._create_snapshot_args(arg)
        if snapshot_args is None:
            return

        print self.dc.vm_create_snapshot(*snapshot_args)

    def do_vm_delete_snapshot(self, arg):
        snapshot_args = self._create_snapshot_args(arg)
        if snapshot_args is None:
            return

        print self.dc.vm_delete_snapshot(*snapshot_args)

    def do_vm_revert_snapshot(self, arg):
        snapshot_args = self._create_snapshot_args(arg)
        if snapshot_args is None:
            return

        print self.dc.vm_revert_snapshot(*snapshot_args)

    def do_check_controller(self, arg):
        self.dc.controller.check()

    def do_show_install_script(self, arg):
        print self.dc.controller.setup_script_provider.generate_setup_script()

    def do_vm_test(self, args):
        result = self.dc.vm_test(args)

        if result.failed:
            print "FAIL", result.data
        else:
            print "SUCCESS", result.data


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
        script_provider.PlainFileProvider(
            script_provider.LocalFilesystem(),
            'install_script.sh',
            'onetime.sh')
        )

    cmd_.dc = datacenter.Datacenter(hv, ctr)
    cmd_.cmdloop()
    hv.disconnect()
    executor.disconnect()
