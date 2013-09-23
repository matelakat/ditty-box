import abc
import textwrap
import StringIO


class SetupScriptProvider(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def generate_setup_script(self):
        pass

    @abc.abstractmethod
    def generate_upstart_script(self):
        pass

    @abc.abstractmethod
    def generate_onetime_script(self):
        pass


class Filesystem(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def contents_of(self, path):
        pass


class FakeFilesystem(Filesystem):
    def __init__(self):
        self.content_by_path = {}

    def contents_of(self, path):
        return self.content_by_path[path]


class LocalFilesystem(Filesystem):
    def contents_of(self, path):
        with open(path, 'rb') as stream:
            return stream.read()


class PlainFileProvider(SetupScriptProvider):
    def __init__(self, filesystem, filename, onetime_script):
        self.filesystem = filesystem
        self.filename = filename
        self.onetime_script_filename = onetime_script

    def generate_setup_script(self):
        return self.filesystem.contents_of(self.filename)

    def generate_upstart_script(self):
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

    def generate_onetime_script(self):
        return StringIO.StringIO(
            self.filesystem.contents_of(self.onetime_script_filename))


class FakeSetupScriptProvider(SetupScriptProvider):
    def generate_setup_script(self):
        return self.fake_setup_script

    def generate_upstart_script(self):
        return self.fake_upstart_script

    def generate_onetime_script(self):
        return self.fake_onetime_script
