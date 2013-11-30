import unittest

from dittybox import path


class TestAbsPath(unittest.TestCase):
    def test_non_abs_path(self):
        with self.assertRaises(path.PathException) as ctx:
            p = path.AbsPath('something')

    def test_multiple_slashes(self):
        self.assertEquals('/', path.AbsPath('/////').path)
        self.assertEquals('/a/b', path.AbsPath('//a///b').path)

    def test_leading_paths_removed(self):
        self.assertEquals('/something', path.AbsPath('/something///').path)


class TestPathElement(unittest.TestCase):
    def test_invalid_character(self):
        with self.assertRaises(path.PathException) as ctx:
            p = path.PathElement('some/non/simple/element')
