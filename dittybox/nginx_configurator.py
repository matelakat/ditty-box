class NginXConfigurator(object):
    def __init__(self, filesystem, config_root, nginx_config_bits):
        self.config_root = config_root
        self.filesystem = filesystem
        self.nginx_config_bits = nginx_config_bits

    def mount_point_of(self, identifier):
        try:
            mountpoint_target = self.filesystem.contents_of(
                '/'.join([self.config_root, identifier]))
            configuration = self.filesystem.contents_of(
                mountpoint_target)
            return mountpoint_target.split('/')[-1]
        except:
            return None


def create(filesystem, config_root, nginx_config_bits):
    return NginXConfigurator(filesystem, config_root, nginx_config_bits)
