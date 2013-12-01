import abc
import collections


RunResult = collections.namedtuple('RunResult', ['stdout', 'sterr', 'return_code'])


class Executor(object):
    __metaclass__ = abc.ABCMeta

    def sudo(self, command):
        return RunResult(*self._sudo(command))

    @abc.abstractmethod
    def _sudo(self, command):
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

    @abc.abstractmethod
    def get(self):
        pass


class FakeExecutor(Executor):
    def __init__(self):
        self.fake_calls = []
        self.fake_sudo_failures = []
        self.sudo_script_results = []
        self.fake_results = {}

    def _sudo(self, command):
        call = (self.sudo, command)
        self.fake_calls.append(call)
        if 'sudo %s' % command in self.fake_results:
            return self.fake_results['sudo %s' % command]
        if call in self.fake_sudo_failures:
            self.fake_sudo_failures.remove(call)
            return None, None, 1
        return None, None, 0

    def sudo_script(self, script):
        self.fake_calls.append((self.sudo_script, script))
        return self.sudo_script_results.pop()

    def disconnect(self):
        raise NotImplementedError()

    def put(self, filelike, remote_location):
        self.fake_calls.append((self.put, filelike, remote_location))

    def wait(self):
        self.fake_calls.append((self.wait,))

    def get(self, path):
        return self.fake_results['get %s' % path]


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

    def _sudo(self, command):
        with self._settings():
            result = fabric_api.sudo(command)
            return result, None, result.return_code

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

            return (
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

    def get(self, path):
        raise NotImplementedError()
