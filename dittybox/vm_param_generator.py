class NoMoreResources(Exception):
    pass


class NameGenerator(object):
    def __init__(self, prefix, first_id, last_id):
        self.prefix = prefix
        self.first_id = first_id
        self.last_id = last_id

    def new_name(self, vm_names):
        for counter in range(self.first_id, self.last_id + 1):
            vm_name = self.prefix + str(counter)
            if vm_name not in vm_names:
                return vm_name
        raise NoMoreResources('No more names are available for new VM')


class FakeNameGenerator(object):
    def __init__(self):
        self.fake_name = None
        self.vm_names = []

    def new_name(self, vm_names):
        self.vm_names.append(vm_names)
        return self.fake_name
