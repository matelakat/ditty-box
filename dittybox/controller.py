import abc
from fabric import api as fabric_api


class Controller(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def unplug_disk(self):
        pass

    @abc.abstractmethod
    def plug_disk(self):
        pass

    @abc.abstractmethod
    def install_to_disk(self):
        pass

    @abc.abstractproperty
    def vm_name(self):
        pass


class Executor(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def sudo(self, command):
        pass

    @abc.abstractmethod
    def sudo_script(self, script, *params):
        pass


class FakeExecutor(Executor):
    def __init__(self):
        self.fake_executed_commands = []
        self.fake_executed_scripts = []

    def sudo(self, command):
        self.fake_executed_commands.append(command)

    def sudo_script(self, script):
        self.fake_executed_scripts.append(script)


class SSHExecutor(Executor):
    def __init__(self, params):
        self.host = params.host
        self.password = password = params.password
        self.ssh_config = params.ssh_config

    def _settings(self):
        return fabric_api.settings(
            host_string=self.host,
            ssh_config_path=self.ssh_config,
            use_ssh_config=True,
            password=self.password,
            eagerly_disconnect=True,
            abort_on_prompts=True)

    def sudo(self, command):
        with self._settings():
            return fabric_api.sudo(command)

    def sudo_script(self, script):
        with self._settings():
            tempfile = fabric_api.sudo('mktemp')
            fabric_api.put(
                local_path=script, remote_path=tempfile, use_sudo=True)
            return fabric_api.sudo('bash %s' % tempfile)


class ShellController(Controller):
    def __init__(self, vm_name, executor, setup_script_provider):
        self.executor = executor
        self._vm_name = vm_name
        self.setup_script_provider = setup_script_provider

    def unplug_disk(self):
        self.executor.sudo('echo "1" > /sys/block/sdb/device/delete')

    def plug_disk(self):
        self.executor.sudo('echo "- - -" > /sys/class/scsi_host/host2/scan')

    def install_to_disk(self):
        self.executor.sudo_script(
            self.setup_script_provider.generate_setup_script())

    @property
    def vm_name(self):
        return self._vm_name


class FakeController(Controller):
    def __init__(self, vm_name, fake_call_collector=None):
        self._vm_name = vm_name
        if fake_call_collector is None:
            fake_call_collector = []
        self.fake_call_collector = fake_call_collector

    @property
    def vm_name(self):
        return self._vm_name

    def plug_disk(self):
        self.fake_call_collector.append(self.plug_disk)

    def unplug_disk(self):
        self.fake_call_collector.append(self.unplug_disk)

    def install_to_disk(self):
        self.fake_call_collector.append(self.install_to_disk)
