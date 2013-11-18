import StringIO
import importlib

from dittybox import config
from dittybox import hypervisor
from dittybox import controller
from dittybox import script_provider
from dittybox import datacenter
from dittybox import cmd_interface


class ConfigException(Exception):
    pass


def create_cmd_interface(config_file_path, filesystem):
    try:
        cfgfile = StringIO.StringIO(filesystem.contents_of(config_file_path))
    except:
        raise ConfigException('Failed to read configuration file')

    try:
        cfg = config.Configuration(cfgfile)
        cmd = cmd_interface.DatacenterCommands()
        cmd._config = cfg
        cmd.prompt = "datacenter [%s] >" % config_file_path
        hypervisor_driver = importlib.import_module(cfg.hypervisor.driver)
        hypervisor.set_hypervisor(hypervisor_driver)

        hv = hypervisor.get_server(cfg.hypervisor.ip, cfg.hypervisor.password)

        executor = controller.SSHExecutor(cfg.controller)
        ctr = controller.ShellController(
            cfg.controller.vm_name,
            executor,
            script_provider.PlainFileProvider(
                filesystem,
                cfg.script_provider.test),
            script_provider.PlainFileInstallScriptProvider(
                filesystem,
                cfg.script_provider.install),
            )

        cmd.dc = datacenter.Datacenter(hv, ctr)

        return cmd

    except config.ConfigFileException as e:
        raise ConfigException(e.message)
