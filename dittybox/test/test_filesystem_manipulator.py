import unittest

from dittybox import filesystem_manipulator
from dittybox import executor


class TestMkdir(unittest.TestCase):
    def test_success(self):
        exc = executor.FakeExecutor()
        manipulator = filesystem_manipulator.FilesystemManipulator(exc)

        result = manipulator.mkdir('some_path')

        self.assertEquals([
            (exc.sudo, 'mkdir -p some_path')], exc.fake_calls)

        self.assertTrue(result.succeeded)

    def test_execution_fails(self):
        exc = executor.FakeExecutor()
        exc.fake_results = {
            'sudo mkdir -p some_path': executor.RunResult('stdout', 'stderr', 1)}
        manipulator = filesystem_manipulator.FilesystemManipulator(exc)

        result = manipulator.mkdir('some_path')

        self.assertFalse(result.succeeded)
        self.assertEquals(
            'standard output: stdout, standard error: stderr, return code: 1',
            result.message)


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

        result = manipulator.rm('some_path')

        self.assertEquals([
            (exc.sudo, 'rm -rf some_path')], exc.fake_calls)

        self.assertTrue(result.succeeded)

    def test_failure(self):
        exc = executor.FakeExecutor()
        exc.fake_results = {
            'sudo rm -rf some_path': executor.RunResult('stdout', 'stderr', 1)}
        manipulator = filesystem_manipulator.FilesystemManipulator(exc)

        result = manipulator.rm('some_path')

        self.assertFalse(result.succeeded)

        self.assertEquals(
            'standard output: stdout, standard error: stderr, return code: 1',
            result.message)
