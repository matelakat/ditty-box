import time
import abc
import StringIO
from fabric import api as fabric_api
from fabric import network as fabric_network


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

    @abc.abstractmethod
    def check(self):
        pass

    @abc.abstractmethod
    def run_script(self, script):
        pass

    @abc.abstractmethod
    def inject_onetime_script(self):
        pass


class Executor(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def sudo(self, command):
        pass

    @abc.abstractmethod
    def sudo_script(self, script, *params):
        pass

    @abc.abstractmethod
    def disconnect(self):
        pass

    @abc.abstractmethod
    def put(self, contents, remote_location):
        pass

    @abc.abstractmethod
    def wait(self):
        pass


class FakeExecutor(Executor):
    def __init__(self):
        self.fake_calls = []
        self.fake_sudo_failures = []

    def sudo(self, command):
        call = (self.sudo, command)
        self.fake_calls.append(call)
        if call in self.fake_sudo_failures:
            self.fake_sudo_failures.remove(call)
            return False
        return True

    def sudo_script(self, script):
        self.fake_calls.append((self.sudo_script, script))

    def disconnect(self):
        raise NotImplementedError()

    def put(self, filelike, remote_location):
        self.fake_calls.append((self.put, filelike, remote_location))

    def wait(self):
        self.fake_calls.append((self.wait,))


class ScriptResult(object):
    def __init__(self, out, err, return_code):
        self.stdout = out
        self.stderr = err
        self.return_code = return_code


class SSHExecutor(Executor):
    def __init__(self, params):
        self.host = params.host
        self.password = password = params.password
        self.ssh_config = params.ssh_config

    def _settings(self):
        return fabric_api.settings(
            fabric_api.hide('stdout'), fabric_api.hide('stderr'),
            host_string=self.host,
            ssh_config_path=self.ssh_config,
            use_ssh_config=True,
            password=self.password,
            eagerly_disconnect=True,
            abort_on_prompts=True,
            warn_only=True,
        )

    def sudo(self, command):
        with self._settings():
            result = fabric_api.sudo(command)
            return result.succeeded

    def sudo_script(self, script):
        script_file = StringIO.StringIO(script)

        with self._settings():
            remote_script = fabric_api.run('mktemp')
            stdout = fabric_api.run('mktemp')
            stderr = fabric_api.run('mktemp')

            fabric_api.put(
                local_path=script_file,
                remote_path=remote_script,
                use_sudo=True)

            with fabric_api.hide('warnings'):
                result = fabric_api.sudo(
                    'bash %s >%s 2>%s </dev/null' % (
                        remote_script, stdout, stderr),
                )

            stdout_file = StringIO.StringIO()
            stderr_file = StringIO.StringIO()

            fabric_api.get(stdout, local_path=stdout_file)
            fabric_api.get(stderr, local_path=stderr_file)

            fabric_api.sudo(
                'rm -f %s %s %s' % (stdout, stderr, remote_script))

            return ScriptResult(
                stdout_file.getvalue(),
                stderr_file.getvalue(),
                result.return_code,
            )

    def disconnect(self):
        fabric_network.disconnect_all()

    def put(self, filelike, remote_location):
        with self._settings():
            fabric_api.put(
                local_path=filelike,
                remote_path=remote_location,
                use_sudo=True)

    def wait(self):
        time.sleep(0.5)


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
        return self.executor.sudo_script(
            self.setup_script_provider.generate_setup_script())

    @property
    def vm_name(self):
        return self._vm_name

    def check(self):
        self.executor.sudo("true")
        self.executor.sudo_script("true")

    def run_script(self, script):
        return self.executor.sudo_script(script)

    def inject_onetime_script(self):
        self.executor.sudo("mkdir -p /mnt/ubuntu")
        self.executor.sudo("mount /dev/sdb1 /mnt/ubuntu")
        self.executor.put(
            self.setup_script_provider.generate_onetime_script(),
            '/mnt/ubuntu/root/install.sh')
        self.executor.put(
            self.setup_script_provider.generate_upstart_script(),
            '/mnt/ubuntu/etc/init/install.conf')
        while not self.executor.sudo("umount /dev/sdb1"):
            self.executor.wait()


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
        return ScriptResult('out', 'err', '0')

    def check(self):
        raise NotImplementedError()

    def run_script(self, script):
        raise NotImplementedError()

    def inject_onetime_script(self):
        raise NotImplementedError()
