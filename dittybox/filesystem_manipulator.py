import StringIO


class Fake(object):
    def __init__(self):
        self.executed_commands = []
        self.raise_errors = {}

    def _add_command(self, command):
        if command in self.raise_errors:
            raise self.raise_errors[command]
        self.executed_commands.append(command)

    def mkdir(self, path):
        self._add_command('mkdir %s' % path)

    def write(self, path, contents):
        self._add_command('write %s %s' % (path, contents))

    def rm(self, path):
        self._add_command('rm %s' % path)


class RemoteFileSystemManipulator(object):
    def __init__(self, executor):
        self.executor = executor

    def mkdir(self, path):
        self.executor.sudo('mkdir -p %s' % path)

    def write(self, path, contents):
        self.executor.put(StringIO.StringIO(contents), path)

    def rm(self, path):
        self.executor.sudo('rm -rf %s' % path)
