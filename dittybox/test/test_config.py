import textwrap
import StringIO

import unittest

from dittybox import config


class TestHypervisorConfig(unittest.TestCase):
    def test_driver(self):
        config_file = StringIO.StringIO(textwrap.dedent("""
        [hypervisor]
        driver = dittybox.esxi
        """))

        cfg = config.Configuration(config_file)

        self.assertEquals('dittybox.esxi', cfg.hypervisor.driver)

    def test_ip(self):
        config_file = StringIO.StringIO(textwrap.dedent("""
        [hypervisor]
        ip = 192.168.9.2
        """))

        cfg = config.Configuration(config_file)

        self.assertEquals('192.168.9.2', cfg.hypervisor.ip)

    def test_password(self):
        config_file = StringIO.StringIO(textwrap.dedent("""
        [hypervisor]
        password = somepassword
        """))

        cfg = config.Configuration(config_file)

        self.assertEquals('somepassword', cfg.hypervisor.password)
