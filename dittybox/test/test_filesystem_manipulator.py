import unittest

from dittybox import filesystem_manipulator
from dittybox import executor


class TestMkdir(unittest.TestCase):
    def test_success(self):
        exc = executor.FakeExecutor()
        manipulator = filesystem_manipulator.FilesystemManipulator(exc)

        manipulator.mkdir('some_path')

        self.assertEquals([
            (exc.sudo, 'mkdir -p some_path')], exc.fake_calls)

    def test_execution_fails(self):
        exc = executor.FakeExecutor()
        exc.fake_results = {
            'sudo mkdir -p some_path': executor.RunResult(None, None, 1)}
        manipulator = filesystem_manipulator.FilesystemManipulator(exc)

        with self.assertRaises(filesystem_manipulator.Error) as ctx:
            manipulator.mkdir('some_path')


class TestWrite(unittest.TestCase):
    def test_success(self):
        exc = executor.FakeExecutor()
        manipulator = filesystem_manipulator.FilesystemManipulator(exc)

        manipulator.write('some_path', 'some_content')

        call, = exc.fake_calls
        cmd, filelike, path = call

        self.assertEquals(exc.put, cmd)
        self.assertEquals('some_content', filelike.read())
        self.assertEquals('some_path', path)


class TestRm(unittest.TestCase):
    def test_success(self):
        exc = executor.FakeExecutor()
        manipulator = filesystem_manipulator.FilesystemManipulator(exc)

        manipulator.rm('some_path')

        self.assertEquals([
            (exc.sudo, 'rm -rf some_path')], exc.fake_calls)
