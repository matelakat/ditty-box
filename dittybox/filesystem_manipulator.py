import StringIO

from dittybox import results


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


class FilesystemManipulator(object):
    def __init__(self, executor):
        self.executor = executor

    def _convert_return_code(self, execution_result):
        if execution_result.return_code != 0:
            return results.Failure(
                'standard output: %s, standard error: %s, return code: %s' %
                    execution_result)
        return results.success()

    def mkdir(self, path):
        return self._convert_return_code(
            self.executor.sudo('mkdir -p %s' % path))

    def write(self, path, contents):
        self.executor.put(StringIO.StringIO(contents), path)

    def rm(self, path):
        return self._convert_return_code(
            self.executor.sudo('rm -rf %s' % path))
