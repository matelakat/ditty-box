import time
import abc
import StringIO
import contextlib
from fabric import api as fabric_api
from fabric import network as fabric_network


class Controller(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def unplug_disk(self):
        pass

    @abc.abstractmethod
    def plug_disk(self):
        pass

    @abc.abstractmethod
    def install_to_disk(self, vm_name):
        pass

    @abc.abstractproperty
    def vm_name(self):
        pass

    @abc.abstractmethod
    def check(self):
        pass

    @abc.abstractmethod
    def run_script(self, script):
        pass

    @abc.abstractmethod
    def inject_onetime_script(self):
        pass

    @abc.abstractmethod
    def upload_data(self, data_provider):
        pass

    @abc.abstractmethod
    def mount_guest_disk(self):
        pass

    @abc.abstractmethod
    def umount_guest_disk(self):
        pass


class ScriptResult(object):
    def __init__(self, out, err, return_code):
        self.stdout = out
        self.stderr = err
        self.return_code = return_code


class ShellController(Controller):
    def __init__(self, vm_name, executor, user_script_provider,
                 install_script_provider):
        self.executor = executor
        self._vm_name = vm_name
        self.user_script_provider = user_script_provider
        self.install_script_provider = install_script_provider

    def unplug_disk(self):
        self.executor.sudo('echo "1" > /sys/block/sdb/device/delete')

    def plug_disk(self):
        self.executor.sudo('echo "- - -" > /sys/class/scsi_host/host2/scan')

    def install_to_disk(self, params):
        return self.executor.sudo_script(
            self.install_script_provider.generate_install_script(params))

    @property
    def vm_name(self):
        return self._vm_name

    def check(self):
        self.executor.sudo("true")
        self.executor.sudo_script("true")

    def run_script(self, script):
        return self.executor.sudo_script(script)

    def mount_guest_disk(self):
        self.executor.sudo("mkdir -p /mnt/ubuntu")
        self.executor.sudo("mount /dev/sdb1 /mnt/ubuntu")

    def umount_guest_disk(self):
        while not self.executor.sudo("umount /dev/sdb1"):
            self.executor.wait()

    def inject_onetime_script(self):
        self.executor.put(
            self.user_script_provider.generate_onetime_stream(),
            '/mnt/ubuntu/root/install.sh')
        self.executor.put(
            self.user_script_provider.generate_upstart_stream(),
            '/mnt/ubuntu/etc/init/install.conf')

    def upload_data(self, data_provider):
        self.executor.sudo('mkdir -p /datacenter_data')
        fname = data_provider.get_md5()
        fpath = "/datacenter_data/%s" % fname
        if not self.executor.sudo('test -f %s' % fpath):
            with contextlib.closing(data_provider.get_stream()) as stream:
                self.executor.put(stream, fpath)
        self.executor.sudo('cp %s /mnt/ubuntu/root/data.blob' % fpath)


class FakeController(Controller):
    def __init__(self, vm_name, fake_call_collector=None):
        self._vm_name = vm_name
        if fake_call_collector is None:
            fake_call_collector = []
        self.fake_call_collector = fake_call_collector

    @property
    def vm_name(self):
        return self._vm_name

    def plug_disk(self):
        self.fake_call_collector.append(self.plug_disk)

    def unplug_disk(self):
        self.fake_call_collector.append(self.unplug_disk)

    def install_to_disk(self, params):
        self.fake_call_collector.append((self.install_to_disk, params))
        return ScriptResult('out', 'err', '0')

    def check(self):
        raise NotImplementedError()

    def run_script(self, script):
        self.fake_call_collector.append(self.run_script)
        return ScriptResult('run_script/out', 'run_script/err', '0')

    def inject_onetime_script(self):
        self.fake_call_collector.append(self.inject_onetime_script)

    def upload_data(self, data_provider):
        self.fake_call_collector.append((self.upload_data, data_provider))

    def mount_guest_disk(self):
        self.fake_call_collector.append(self.mount_guest_disk)

    def umount_guest_disk(self):
        self.fake_call_collector.append(self.umount_guest_disk)
