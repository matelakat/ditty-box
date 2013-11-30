import collections


class Result(object):
    def __init__(self, succeeded, message=None):
        self._succeeded = succeeded
        self.message = message

    @property
    def succeeded(self):
        return self._succeeded


class Success(Result):
    def __init__(self):
        super(Success, self).__init__(True)


class Failure(Result):
    def __init__(self, message):
        super(Failure, self).__init__(False, message)


class SuccessListing(Success):
    def __init__(self, mounts):
        super(SuccessListing, self).__init__()
        self.mounts = mounts


class Mount(collections.namedtuple("Mount", ["identifier", "location"])):
    @property
    def is_degenerate(self):
        return None in [self.identifier, self.location]


class NginXConfigurator(object):
    def __init__(self, filesystem, filesystem_manipulator, config_root,
                 nginx_config_bits, config_generator):
        self.config_root = config_root
        self.filesystem = filesystem
        self.nginx_config_bits = nginx_config_bits
        self.filesystem_manipulator = filesystem_manipulator
        self.config_generator = config_generator

    def add_mount(self, mount):
        resource_path = '/'.join([self.config_root, mount.identifier])
        location_path = '/'.join([self.nginx_config_bits, mount.location])
        try:
            contents = self.filesystem.contents_of(location_path)
            return Failure('%s already mounted' % mount.location)
        except:
            pass
        try:
            self.filesystem_manipulator.write(
                resource_path,
                location_path)
            self.filesystem_manipulator.write(
                location_path,
                self.config_generator(mount.location))
        except Exception as e:
            return Failure(e.message)
        return Success()

    def list_mounts(self):
        result = []
        locations = self.filesystem.ls(self.nginx_config_bits)
        resources = self.filesystem.ls(self.config_root)
        locations_done = []

        for resource in resources:
            location = self.filesystem.contents_of(
                '/'.join([self.config_root, resource]))
            if location in locations:
                result.append(Mount(resource, location))
                locations_done.append(location)
            else:
                result.append(Mount(resource, None))

        for location in locations:
            if location in locations_done:
                continue
            result.append(Mount(None, location))

        return SuccessListing(result)

    def delete_mount(self, mount):
        if mount.is_degenerate:
            return Failure('degenerate mount')

        if mount not in self.list_mounts().mounts:
            return Failure('non existing mount')

        resource_path = '/'.join([self.config_root, mount.identifier])
        config_path = '/'.join([self.nginx_config_bits, mount.location])

        self.filesystem_manipulator.rm(config_path)
        self.filesystem_manipulator.rm(resource_path)
        return Success()


def fake_config_generator(location):
    return "config-for %s" % location


def create(filesystem, filesystem_manipulator, config_root, nginx_config_bits,
           config_generator):
    return NginXConfigurator(
        filesystem, filesystem_manipulator, config_root, nginx_config_bits, config_generator)
