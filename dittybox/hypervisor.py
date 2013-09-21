_IMPL = None


class VM(object):
    def __init__(self, name, power_state):
        self.name = name
        self.power_state = power_state


def get_server(host, password):
    return _IMPL.get_server(host, password)


def set_hypervisor(impl):
    global _IMPL
    _IMPL = impl
