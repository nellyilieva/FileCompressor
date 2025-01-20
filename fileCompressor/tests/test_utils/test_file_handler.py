import unittest
import os
from pathlib import Path
from utils.file_handler import FileHandler


class TestFileHandler(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(__file__).parent.parent / 'test_files'
        self.test_dir.mkdir(exist_ok=True)

        self.test_file = self.test_dir / 'test.txt'
        with open(self.test_file, 'wb') as f:
            f.write(b'Hello, World!' * 1000)

        self.handler = FileHandler(chunk_size=100)

    def tearDown(self):
        if self.test_file.exists():
            self.test_file.unlink()

    def test_open_close_file(self):
        self.handler.open_file(self.test_file, 'rb')
        self.assertIsNotNone(self.handler._current_file)
        self.handler.close_file()
        self.assertIsNone(self.handler._current_file)

        self.handler.open_file(self.test_file, 'wb')
        self.assertIsNotNone(self.handler._current_file)
        self.handler.close_file()

    def test_read_chunks(self):
        self.handler.open_file(self.test_file, 'rb')
        chunks = list(self.handler.read_chunks())

        expected_chunks = (os.path.getsize(self.test_file) + 99) // 100
        self.assertEqual(len(chunks), expected_chunks)

        with open(self.test_file, 'rb') as f:
            original = f.read()
        self.assertEqual(b''.join(chunks), original)

    def test_write_chunk(self):
        test_data = b'Test data' * 20
        output_file = self.test_dir / 'output.txt'

        self.handler.open_file(output_file, 'wb')
        for i in range(0, len(test_data), 100):
            chunk = test_data[i:i + 100]
            self.handler.write_chunk(chunk)
        self.handler.close_file()

        with open(output_file, 'rb') as f:
            written_data = f.read()
        self.assertEqual(written_data, test_data)

        output_file.unlink()

    def test_context_manager(self):
        with FileHandler() as handler:
            handler.open_file(self.test_file, 'rb')
            chunks = list(handler.read_chunks())
            self.assertGreater(len(chunks), 0)

        self.assertIsNone(handler._current_file)

    def test_error_handling(self):
        with self.assertRaises(IOError):
            next(self.handler.read_chunks())

        with self.assertRaises(IOError):
            self.handler.write_chunk(b'test')

        with self.assertRaises(IOError):
            self.handler.open_file(Path('nonexistent.txt'), 'rb')
