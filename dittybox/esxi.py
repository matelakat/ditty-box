from pysphere import VIServer


def get_server(host, password):
    server = VIServer()
    server.connect(host, "root", password)
    return server
