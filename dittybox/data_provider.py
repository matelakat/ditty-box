import abc
import hashlib


class DataProvider(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_md5(self):
        pass

    @abc.abstractmethod
    def get_stream(self):
        pass


class SimpleDataProvider(DataProvider):
    def __init__(self, filesystem, data_path, buffer_size=1024):
        self.filesystem = filesystem
        self.buffer_size = buffer_size
        self.data_path = data_path

    def get_md5(self):
        m = hashlib.md5()
        handle = self.filesystem.stream_of(self.data_path)
        while True:
            data = handle.read(self.buffer_size)
            if data:
                m.update(data)
            else:
                handle.close()
                return m.hexdigest()

    def get_stream(self):
        return self.filesystem.stream_of(self.data_path)


class FakeDataProvider(DataProvider):
    def get_md5(self):
        return self.fake_md5sum

    def get_stream(self):
        return self.fake_stream
