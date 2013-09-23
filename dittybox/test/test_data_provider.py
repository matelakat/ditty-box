import unittest
import hashlib

from dittybox import data_provider
from dittybox import filesystem


class TestDataProvider(unittest.TestCase):
    def test_md5_report(self):
        fs = filesystem.FakeFilesystem()
        fs.content_by_path['somepath'] = 'somedata'

        m = hashlib.md5()
        m.update('somedata')
        digest = m.hexdigest()

        dp = data_provider.SimpleDataProvider(fs, 'somepath')

        self.assertEquals(digest, dp.get_md5())

        self.assertEquals(0, fs.open_files)

    def test_get_stream(self):
        fs = filesystem.FakeFilesystem()
        fs.content_by_path['somepath'] = 'somedata'
        dp = data_provider.SimpleDataProvider(fs, 'somepath')

        self.assertEquals('somedata', dp.get_stream().read())

