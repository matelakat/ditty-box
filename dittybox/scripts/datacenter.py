import argparse
import cmd
import importlib


from dittybox import config
from dittybox import hypervisor
from dittybox import datacenter
from dittybox import controller
from dittybox import script_provider
from dittybox import filesystem
from dittybox import data_provider


class DatacenterCommands(cmd.Cmd):
    def do_exit(self, arg):
        return True

    def do_network_list(self, arg):
        for network_name in self.dc.list_networks():
            print network_name

    def do_vm_list(self, arg):
        for vm_name, pwr in self.dc.list_vms():
            print vm_name, pwr

    def do_vm_create(self, arg):
        params = self._create_create_vm_args(arg)
        if not params:
            return
        mem_megs, disk_megs, network = params
        vm_name = self.dc.vm_create(mem_megs, disk_megs, network)
        print vm_name

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

    def _create_create_vm_args(self, arg):
        if len(arg.split(',')) != 3:
            print "Three arguments needed: mem_megs, disk_megs, network"
            return None

        mem_megs, disk_megs, network = [a.strip() for a in arg.split(',')]
        return (int(mem_megs), int(disk_megs), network)


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
        result = self.dc.vm_test(
            args,
            data_provider.SimpleDataProvider(
                filesystem.LocalFilesystem(),
                self._config.data_provider.data_file)
            )

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
    cmd_._config = cfg
    cmd_.prompt = "datacenter [%s] >" % args.config

    hypervisor_driver = importlib.import_module(cfg.hypervisor.driver)
    hypervisor.set_hypervisor(hypervisor_driver)

    hv = hypervisor.get_server(cfg.hypervisor.ip, cfg.hypervisor.password)

    executor = controller.SSHExecutor(cfg.controller)
    ctr = controller.ShellController(
        cfg.controller.vm_name,
        executor,
        script_provider.PlainFileProvider(
            filesystem.LocalFilesystem(),
            cfg.script_provider.install,
            cfg.script_provider.test)
        )

    cmd_.dc = datacenter.Datacenter(hv, ctr)
    cmd_.cmdloop()
    hv.disconnect()
    executor.disconnect()
