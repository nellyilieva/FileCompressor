import unittest
from core.interfaces.compressor import BaseCompressor


class TestCompressor(unittest.TestCase):
    """Test cases for the BaseCompressor interface"""

    def test_base_compressor_is_abstract(self):
        with self.assertRaises(TypeError):
            BaseCompressor()

    def test_compressor_interface_methods(self):
        abstract_methods = BaseCompressor.__abstractmethods__
        required_methods = {'compress', 'decompress', 'get_compression_stats'}
        self.assertEqual(required_methods, abstract_methods)
