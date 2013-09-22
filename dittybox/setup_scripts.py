import abc


class SetupScriptProvider(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def generate_setup_script(self):
        pass


class PlainFileProvider(SetupScriptProvider):
    def __init__(self, filename):
        self.filename = filename

    def generate_setup_script(self):
        with open(self.filename, 'rb') as script_file:
            return script_file.read()


class FakeSetupScriptProvider(SetupScriptProvider):
    def generate_setup_script(self):
        return self.fake_setup_script
