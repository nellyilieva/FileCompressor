import unittest
from core.interfaces.ui import BaseUI


class TestUI(unittest.TestCase):
    """Test cases for the BaseUI interface"""

    def test_base_ui_is_abstract(self):
        with self.assertRaises(TypeError):
            BaseUI()

    def test_ui_interface_methods(self):
        abstract_methods = BaseUI.__abstractmethods__
        required_methods = {'start', 'process_file', 'update_progress',
                            'show_error', 'show_stats'}
        self.assertEqual(required_methods, abstract_methods)


if __name__ == '__main__':
    unittest.main()
