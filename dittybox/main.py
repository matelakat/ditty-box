import StringIO
import importlib

from dittybox import config
from dittybox import hypervisor
from dittybox import controller
from dittybox import script_provider
from dittybox import datacenter
from dittybox import cmd_interface
from dittybox import data_provider
from dittybox import vm_param_generator


class ConfigException(Exception):
    pass


def create_cmd_interface(config_file_path, filesystem):
    try:
        cfgfile = StringIO.StringIO(filesystem.contents_of(config_file_path))
    except:
        raise ConfigException('Failed to read configuration file')

    try:
        cfg = config.Configuration(cfgfile)
        hypervisor_driver = importlib.import_module(cfg.hypervisor.driver)
        hypervisor.set_hypervisor(hypervisor_driver)

        hv = hypervisor.get_server(cfg.hypervisor.ip, cfg.hypervisor.password)

        executor = controller.SSHExecutor(cfg.controller)
        ctr = controller.ShellController(
            cfg.controller.vm_name,
            executor,
            script_provider.PlainFileProvider(
                filesystem,
                cfg.user_script_provider.script_path),
            script_provider.PlainFileInstallScriptProvider(
                filesystem,
                cfg.script_providers.install),
            )

        cmd = cmd_interface.create(
            config_file_path,
            data_provider.SimpleDataProvider(
                filesystem, cfg.data_provider.data_file),
            datacenter.Datacenter(hv, ctr,
                vm_param_generator.NameGenerator(
                    cfg.name_generator.prefix,
                    int(cfg.name_generator.first_id),
                    int(cfg.name_generator.last_id),
                    )
                ),
            )

        return cmd

    except config.ConfigFileException as e:
        raise ConfigException(e.message)
