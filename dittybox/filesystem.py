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

    @abc.abstractmethod
    def ls(self, path):
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

    def ls(self, root_path):
        root_path_elements = root_path.split('/')
        results = []
        for path in self.content_by_path:
            path_elements = path.split('/')

            if path_elements[0:len(root_path_elements)] == root_path_elements:
                results.append(path_elements[len(root_path_elements)])

        return results


class LocalFilesystem(Filesystem):
    def contents_of(self, path):
        with open(path, 'rb') as stream:
            return stream.read()

    def stream_of(self, path):
        return open(path, 'rb')

    def ls(self, path):
        raise NotImplementedError()


class RemoteFilesystem(Filesystem):
    def __init__(self, executor):
        self.executor = executor

    def contents_of(self, path):
        return self.executor.get(path)

    def stream_of(self, path):
        return StringIO.StringIO(self.contents_of(path))

    def ls(self, path):
        ls_results = self.executor.sudo('ls -1 %s' % path)
        return ls_results.stdout.split('\n')
