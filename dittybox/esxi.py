from pysphere import VIServer

from dittybox import hypervisor


class ESXiServer(hypervisor.Server):
    def __init__(self, viserver):
        self.viserver = viserver

    @property
    def vms(self):
        props = self.viserver._retrieve_properties_traversal(
            property_names=['config.name', 'runtime.powerState'],
            obj_type="VirtualMachine")

        for prop_set in props:
            name = prop_set.PropSet[0].Val
            power_state = prop_set.PropSet[1].Val
            yield hypervisor.VM(name, power_state)

    def disconnect(self):
        self.viserver.disconnect()



def get_server(host, password):
    server = VIServer()
    server.connect(host, "root", password)
    return ESXiServer(server)
