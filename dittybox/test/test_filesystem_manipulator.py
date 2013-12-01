import unittest

from dittybox import filesystem_manipulator
from dittybox import executor


class TestMkdir(unittest.TestCase):
    def test_success(self):
        exc = executor.FakeExecutor()
        manipulator = filesystem_manipulator.RemoteFileSystemManipulator(exc)

        manipulator.mkdir('some_path')

        self.assertEquals([
            (exc.sudo, 'mkdir -p some_path')], exc.fake_calls)
