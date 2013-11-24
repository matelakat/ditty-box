import abc
import textwrap
import StringIO


class InstallScriptProvider(object):
    __metaclass__ = abc.ABCMeta

    def generate_install_script(self, params):
        return self._generate_install_script(params)

    @abc.abstractmethod
    def _generate_install_script(self, params):
        pass


class SetupScriptProvider(object):
    @abc.abstractmethod
    def generate_upstart_stream(self):
        pass

    @abc.abstractmethod
    def generate_onetime_stream(self):
        pass


class PlainFileInstallScriptProvider(InstallScriptProvider):

    def __init__(self, filesystem, setup_script_path):
        self.filesystem = filesystem
        self.setup_script_path = setup_script_path

    def _generate_install_script(self, params):
        return self.filesystem.contents_of(self.setup_script_path)


class TemplateBasedInstallScriptProvider(InstallScriptProvider):

    def __init__(self, filesystem, script_path):
        self.filesystem = filesystem
        self.script_path = script_path

    def _generate_install_script(self, params):
        script = self.filesystem.contents_of(self.script_path)
        for k, v in params.items():
            script = script.replace('@%s@' % k, v)
        return script


class PlainFileProvider(SetupScriptProvider):
    def __init__(self, filesystem, script_path):
        self.filesystem = filesystem
        self.script_path = script_path

    def generate_upstart_stream(self):
        return StringIO.StringIO(textwrap.dedent('''
        start on runlevel [2345]

        task

        script
            echo "install started" >> /root/install.log
            /bin/bash /root/install.sh </dev/null >/root/install.stdout 2>/root/install.stderr || true
            halt -p
            echo "install finished" >> /root/install.log
        end script
        '''))

    def generate_onetime_stream(self):
        return StringIO.StringIO(
            self.filesystem.contents_of(self.script_path))


class FakeInstallScriptProvider(InstallScriptProvider):
    def _generate_install_script(self, params):
        params = ','.join(sorted(['='.join(item) for item in params.items()]))
        return ':'.join([self.fake_setup_script, params])


class FakeSetupScriptProvider(SetupScriptProvider):
    def generate_upstart_stream(self):
        return self.fake_upstart_script

    def generate_onetime_stream(self):
        return self.fake_onetime_script
