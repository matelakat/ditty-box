class Datacenter(object):
    def __init__(self, hypervisor):
        self.hypervisor = hypervisor

    def list_vms(self):
        result = []
        for vm in self.hypervisor.vms:
            result.append((vm.name, 'OFF' if vm.powered_off else 'NOT OFF'))
        return result
