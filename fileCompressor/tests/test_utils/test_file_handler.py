import unittest
from pathlib import Path
import os
from utils.file_handler import FileHandler


class TestFileHandler(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(__file__).parent.parent / 'test_files'
        self.test_dir.mkdir(exist_ok=True)

        self.test_file = self.test_dir / 'test.txt'
        with open(self.test_file, 'wb') as f:
            f.write(b'Some text bla' * 1000)

        self.handler = FileHandler(chunk_size=100)

    def tearDown(self):
        if hasattr(self, 'handler'):
            self.handler.close_file()

        try:
            if self.test_file.exists():
                self.test_file.unlink()
        except PermissionError:
            pass

    def test_open_close_file(self):
        self.handler.open_file(self.test_file, 'rb')
        self.assertTrue(self.handler.is_open)
        self.handler.close_file()
        self.assertFalse(self.handler.is_open)

        self.handler.open_file(self.test_file, 'wb')
        self.assertTrue(self.handler.is_open)
        self.handler.close_file()
        self.assertFalse(self.handler.is_open)

    def test_chunk_size_property(self):
        self.assertEqual(self.handler.chunk_size, 100)

        self.handler.chunk_size = 200
        self.assertEqual(self.handler.chunk_size, 200)

        with self.assertRaises(ValueError):
            self.handler.chunk_size = 0
        with self.assertRaises(ValueError):
            self.handler.chunk_size = -100

    def test_file_size_property(self):
        self.handler.open_file(self.test_file, 'rb')
        self.assertEqual(self.handler.file_size, os.path.getsize(self.test_file))
        self.handler.close_file()

    def test_is_open_property(self):
        self.assertFalse(self.handler.is_open)

        self.handler.open_file(self.test_file, 'rb')
        self.assertTrue(self.handler.is_open)

        self.handler.close_file()
        self.assertFalse(self.handler.is_open)

    def test_read_chunks(self):
        self.handler.open_file(self.test_file, 'rb')
        chunks = []

        while True:
            chunk = self.handler.read_chunk(self.handler.chunk_size)
            if not chunk:
                break
            chunks.append(chunk)

        expected_chunks = (os.path.getsize(self.test_file) + 99) // 100
        self.assertEqual(len(chunks), expected_chunks)

        with open(self.test_file, 'rb') as f:
            original = f.read()
        self.assertEqual(b''.join(chunks), original)
        self.handler.close_file()

    def test_write_chunk(self):
        test_data = b'More text' * 20
        output_file = self.test_dir / 'output.txt'

        try:
            self.handler.open_file(output_file, 'wb')
            for i in range(0, len(test_data), 100):
                chunk = test_data[i:i + 100]
                self.handler.write_chunk(chunk)
            self.handler.close_file()

            with open(output_file, 'rb') as f:
                written_data = f.read()
            self.assertEqual(written_data, test_data)

        finally:
            if output_file.exists():
                output_file.unlink()

    def test_context_manager(self):
        with FileHandler() as handler:
            handler.open_file(self.test_file, 'rb')
            chunks = []
            while True:
                chunk = handler.read_chunk(100)
                if not chunk:
                    break
                chunks.append(chunk)
            self.assertGreater(len(chunks), 0)
        self.assertIsNone(handler._current_file)

    def test_error_handling(self):
        with self.assertRaises(IOError):
            self.handler.read_chunk(100)
        with self.assertRaises(IOError):
            self.handler.write_chunk(b'test')
        with self.assertRaises(IOError):
            self.handler.open_file(Path('nonexistent.txt'), 'rb')


if __name__ == '__main__':
    unittest.main()
