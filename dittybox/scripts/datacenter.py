import argparse

from dittybox import filesystem
from dittybox import main as dittybox_main


def main():
    parser = argparse.ArgumentParser(description='Datacenter shell')
    parser.add_argument('config', help='Configuration file')
    args = parser.parse_args()

    cmd = dittybox_main.create_cmd_interface(
        args.config, filesystem.LocalFilesystem())

    cmd.cmdloop()
    cmd.dc.hypervisor.disconnect()
    cmd.dc.controller.executor.disconnect()
