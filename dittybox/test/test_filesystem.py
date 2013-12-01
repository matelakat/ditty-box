import unittest

from dittybox import filesystem
from dittybox import executor


class TestLs(unittest.TestCase):
    def test_listing(self):
        fs = filesystem.FakeFilesystem()
        fs.content_by_path = {
            '/1/a/3': 1,
            '/1/b/c': 2,
        }

        self.assertEquals(['a', 'b'], fs.ls('/1'))


class RemoteFileSystem(unittest.TestCase):
    def test_contents_of(self):
        xec = executor.FakeExecutor()
        xec.fake_results = {
            'get somepath': 'somecontent'
        }

        fs = filesystem.RemoteFilesystem(xec)

        self.assertEquals('somecontent', fs.contents_of('somepath'))

    def test_stream_of(self):
        xec = executor.FakeExecutor()
        xec.fake_results = {
            'get somepath': 'somecontent'
        }

        fs = filesystem.RemoteFilesystem(xec)

        self.assertEquals('somecontent', fs.stream_of('somepath').read())

    def test_ls(self):
        xec = executor.FakeExecutor()
        xec.fake_results = {
            'sudo ls -1 somepath': ('f1\nf2\nf3', None, 0),
        }

        fs = filesystem.RemoteFilesystem(xec)

        self.assertEquals(['f1', 'f2', 'f3'], fs.ls('somepath'))
