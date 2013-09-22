import abc


class SetupScriptProvider(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def generate_setup_script(self):
        pass


class FakeSetupScriptProvider(SetupScriptProvider):
    def generate_setup_script(self):
        return self.fake_setup_script
