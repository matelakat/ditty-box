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



class NginXConfigurator(object):
    def __init__(self, filesystem, filesystem_manipulator, config_root,
                 nginx_config_bits, config_generator):
        self.config_root = config_root
        self.filesystem = filesystem
        self.nginx_config_bits = nginx_config_bits
        self.filesystem_manipulator = filesystem_manipulator
        self.config_generator = config_generator

    def mount_point_of(self, identifier):
        try:
            mountpoint_target = self.filesystem.contents_of(
                '/'.join([self.config_root, identifier]))
            configuration = self.filesystem.contents_of(
                mountpoint_target)
            return mountpoint_target.split('/')[-1]
        except:
            return None

    def set_mountpoint(self, identifier, location):
        resource_path = '/'.join([self.config_root, identifier])
        location_path = '/'.join([self.nginx_config_bits, location])
        try:
            contents = self.filesystem.contents_of(location_path)
            return Failure('%s already mounted' % location)
        except:
            pass
        try:
            self.filesystem_manipulator.write(
                resource_path,
                location_path)
            self.filesystem_manipulator.write(
                location_path,
                self.config_generator(location))
        except Exception as e:
            return Failure(e.message)
        return Success()

    def list_mounts(self):
        return SuccessListing([])


def fake_config_generator(location):
    return "config-for %s" % location


def create(filesystem, filesystem_manipulator, config_root, nginx_config_bits,
           config_generator):
    return NginXConfigurator(
        filesystem, filesystem_manipulator, config_root, nginx_config_bits, config_generator)
