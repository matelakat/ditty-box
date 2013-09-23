import abc
import StringIO


class Filesystem(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def contents_of(self, path):
        pass

    @abc.abstractmethod
    def stream_of(self, path):
        pass


class FileWrapper(object):
    def __init__(self, filesystem, wrapped):
        self.filesystem = filesystem
        self.wrapped = wrapped

    def close(self):
        self.filesystem.open_files -= 1

    def read(self, *args):
        return self.wrapped.read(*args)


class FakeFilesystem(Filesystem):
    def __init__(self):
        self.content_by_path = {}
        self.open_files = 0

    def contents_of(self, path):
        return self.content_by_path[path]

    def stream_of(self, path):
        stream = StringIO.StringIO(self.contents_of(path))
        self.open_files += 1
        return FileWrapper(self, stream)


class LocalFilesystem(Filesystem):
    def contents_of(self, path):
        with open(path, 'rb') as stream:
            return stream.read()
