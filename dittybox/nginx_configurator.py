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


class Mount(collections.namedtuple("Mount", ["resource", "location"])):
    @property
    def is_degenerate(self):
        return None in [self.resource, self.location]


class PathElement(object):
    def __init__(self, path_element):
        self._path_element = path_element

    @property
    def path_element(self):
        return self._path_element


class AbsPath(object):
    def __init__(self, path):
        self._path = path

    @property
    def path(self):
        return self._path

    def elements(self):
        return '/'.split(self._path)

    def __add__(self, other):
        if hasattr(other, 'path_element'):
            return AbsPath(self.path + '/' + other.path_element)


class NginXConfigurator(object):
    MSG_DEGENERATE_MOUNT = 'degenerate mount'

    def __init__(self, filesystem, filesystem_manipulator, config_root,
                 nginx_config_bits, config_generator):
        self.config_root = AbsPath(config_root)
        self.filesystem = filesystem
        self.nginx_config_bits = AbsPath(nginx_config_bits)
        self.filesystem_manipulator = filesystem_manipulator
        self.config_generator = config_generator

    def add_mount(self, mount):
        if mount.is_degenerate:
            return Failure(self.MSG_DEGENERATE_MOUNT)

        existing_mounts = self.list_mounts().mounts
        for existing_mount in existing_mounts:
            if mount.location == existing_mount.location:
                return Failure('%s already mounted' % mount.location)

        resource_path = (self.config_root + PathElement(mount.resource)).path
        location_path = (self.nginx_config_bits + PathElement(mount.location)).path
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
        locations = self.filesystem.ls(self.nginx_config_bits.path)
        resources = self.filesystem.ls(self.config_root.path)
        locations_done = []

        for resource in resources:
            location = self.filesystem.contents_of(
                (self.config_root + PathElement(resource)).path)
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
            return Failure(self.MSG_DEGENERATE_MOUNT)

        if mount not in self.list_mounts().mounts:
            return Failure('non existing mount')

        resource_path = (self.config_root + PathElement(mount.resource)).path
        config_path = (self.nginx_config_bits + PathElement(mount.location)).path

        self.filesystem_manipulator.rm(config_path)
        self.filesystem_manipulator.rm(resource_path)
        return Success()


def fake_config_generator(location):
    return "config-for %s" % location


def create(filesystem, filesystem_manipulator, config_root, nginx_config_bits,
           config_generator):
    return NginXConfigurator(
        filesystem, filesystem_manipulator, config_root, nginx_config_bits, config_generator)
