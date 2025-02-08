import unittest
from pathlib import Path
import os
from utils.file_handler import FileHandler


class TestFileHandler(unittest.TestCase):
    def setUp(self):
        """Set up test files"""
        self.test_dir = Path(__file__).parent.parent / 'test_files'
        self.test_dir.mkdir(exist_ok=True)

        # Create test file with some data
        self.test_file = self.test_dir / 'test.txt'
        with open(self.test_file, 'wb') as f:
            f.write(b'Hello, World!' * 1000)

        self.handler = FileHandler(chunk_size=100)

    def tearDown(self):
        """Clean up test files"""
        if hasattr(self, 'handler'):
            self.handler.close_file()

        try:
            if self.test_file.exists():
                self.test_file.unlink()
        except PermissionError:
            pass

    def test_open_close_file(self):
        """Test opening and closing files"""
        self.handler.open_file(self.test_file, 'rb')
        self.assertIsNotNone(self.handler._current_file)
        self.handler.close_file()
        self.assertIsNone(self.handler._current_file)
        self.handler.open_file(self.test_file, 'wb')
        self.assertIsNotNone(self.handler._current_file)
        self.handler.close_file()

    def test_chunk_size_property(self):
        """Test chunk_size getter and setter"""
        self.assertEqual(self.handler.chunk_size, 100)

        self.handler.chunk_size = 200
        self.assertEqual(self.handler.chunk_size, 200)

        with self.assertRaises(ValueError):
            self.handler.chunk_size = 0
        with self.assertRaises(ValueError):
            self.handler.chunk_size = -100

    def test_file_size_property(self):
        """Test file_size getter"""
        self.handler.open_file(self.test_file, 'rb')
        self.assertEqual(self.handler.file_size, os.path.getsize(self.test_file))
        self.handler.close_file()

    def test_is_open_property(self):
        """Test is_open property"""
        self.assertFalse(self.handler.is_open)

        self.handler.open_file(self.test_file, 'rb')
        self.assertTrue(self.handler.is_open)

        self.handler.close_file()
        self.assertFalse(self.handler.is_open)

    def test_read_chunks(self):
        """Test reading file in chunks"""
        with self.handler:
            self.handler.open_file(self.test_file, 'rb')
            chunks = list(self.handler.read_chunks())

            expected_chunks = (os.path.getsize(self.test_file) + 99) // 100
            self.assertEqual(len(chunks), expected_chunks)

            with open(self.test_file, 'rb') as f:
                original = f.read()
            self.assertEqual(b''.join(chunks), original)

    def test_write_chunk(self):
        """Test writing chunks to file"""
        test_data = b'Test data' * 20
        output_file = self.test_dir / 'output.txt'

        try:
            with self.handler:
                self.handler.open_file(output_file, 'wb')
                for i in range(0, len(test_data), 100):
                    chunk = test_data[i:i + 100]
                    self.handler.write_chunk(chunk)

            with open(output_file, 'rb') as f:
                written_data = f.read()
            self.assertEqual(written_data, test_data)

        finally:
            if output_file.exists():
                output_file.unlink()

    def test_context_manager(self):
        """Test context manager functionality"""
        with FileHandler() as handler:
            handler.open_file(self.test_file, 'rb')
            chunks = list(handler.read_chunks())
            self.assertGreater(len(chunks), 0)
        self.assertIsNone(handler._current_file)

    def test_error_handling(self):
        """Test error handling cases"""
        with self.assertRaises(IOError):
            next(self.handler.read_chunks())
        with self.assertRaises(IOError):
            self.handler.write_chunk(b'test')
        with self.assertRaises(IOError):
            self.handler.open_file(Path('nonexistent.txt'), 'rb')