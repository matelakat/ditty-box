class PathException(Exception):
    pass


class AbsPath(object):
    def __init__(self, path):
        if not path.startswith('/'):
            raise PathException()
        self._path = '/' + '/'.join(p for p in path.split('/') if p)

    @property
    def path(self):
        return self._path

    def elements(self):
        return '/'.split(self._path)

    def __add__(self, other):
        if hasattr(other, 'path_element'):
            return AbsPath(self.path + '/' + other.path_element)


class PathElement(object):
    def __init__(self, path_element):
        if '/' in path_element:
            raise PathException()
        self._path_element = path_element

    @property
    def path_element(self):
        return self._path_element
