import unittest
from dittybox import nginx_configurator


class TestNginXConfigurator(unittest.TestCase):
    def test_constructor(self):
        configurator = nginx_configurator.create()
