_IMPL = None


def get_server(host, password):
    return _IMPL.get_server(host, password)


def set_hypervisor(impl):
    global _IMPL
    _IMPL = impl
