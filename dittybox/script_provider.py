import abc
import textwrap
import StringIO


class SetupScriptProvider(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def generate_setup_script(self):
        pass

    @abc.abstractmethod
    def generate_upstart_stream(self):
        pass

    @abc.abstractmethod
    def generate_onetime_stream(self):
        pass


class PlainFileProvider(SetupScriptProvider):
    def __init__(self, filesystem, setup_script_path, onetime_script_path):
        self.filesystem = filesystem
        self.setup_script_path = setup_script_path
        self.onetime_script_path = onetime_script_path

    def generate_setup_script(self):
        return self.filesystem.contents_of(self.setup_script_path)

    def generate_upstart_stream(self):
        return StringIO.StringIO(textwrap.dedent('''
        start on runlevel [2345]

        task

        script
            echo "install started" >> /root/install.log
            /bin/bash /root/install.sh </dev/null >/root/install.stdout 2>/root/install.stderr
            halt -p
            echo "install finished" >> /root/install.log
        end script
        '''))

    def generate_onetime_stream(self):
        return StringIO.StringIO(
            self.filesystem.contents_of(self.onetime_script_path))


class FakeSetupScriptProvider(SetupScriptProvider):
    def generate_setup_script(self):
        return self.fake_setup_script

    def generate_upstart_stream(self):
        return self.fake_upstart_script

    def generate_onetime_stream(self):
        return self.fake_onetime_script
