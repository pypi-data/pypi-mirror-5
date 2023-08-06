import os
import unittest
import tempfile

from kuyruk.config import Config
from kuyruk.master import parse_queues_str
from kuyruk.test import config as user_config


class ConfigTestCase(unittest.TestCase):

    def test_from_pyfile(self):
        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, 'config.py')
        config = Config()
        config.from_pyfile(path)
        self.assertEqual(config.MAX_LOAD, 20)

    def test_from_object(self):
        user_config.MAX_LOAD = 21
        config = Config()
        config.from_object(user_config)
        self.assertEqual(config.MAX_LOAD, 21)

    def test_export(self):
        config = Config()
        config.RABBIT_PORT = 1234
        fd, path = tempfile.mkstemp()
        os.close(fd)
        config.export(path)
        with open(path) as f:
            content = f.read()
        print content
        assert 'RABBIT_PORT = 1234' in content

        config = Config()
        config.from_pyfile(path)
        assert config.RABBIT_PORT == 1234
        os.unlink(path)

    def test_queues_string(self):
        assert parse_queues_str(" a,b, c, 2*d, e*3, 2*@f ") == \
            ['a', 'b', 'c', 'd', 'd', 'e', 'e', 'e', '@f', '@f']
