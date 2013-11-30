import unittest

from dittybox import filesystem


class TestLs(unittest.TestCase):
    def test_listing(self):
        fs = filesystem.FakeFilesystem()
        fs.content_by_path = {
            '/1/a/3': 1,
            '/1/b/c': 2,
        }

        self.assertEquals(['a', 'b'], fs.ls('/1'))
