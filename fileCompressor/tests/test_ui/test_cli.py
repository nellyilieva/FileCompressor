import unittest
from pathlib import Path
import tempfile
import shutil
import os
from ui.cli.command_line import format_size, get_file_info, process_file
from compressors.rle import RLECompressor


class TestCLI(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.compressor = RLECompressor()

    def tearDown(self):
        """Clean up test environment after each test"""
        shutil.rmtree(self.temp_dir)

    def create_test_file(self, content: bytes) -> Path:
        """Create a test file with given content"""
        file_path = Path(self.temp_dir) / "test_file.txt"
        with open(file_path, 'wb') as f:
            f.write(content)
        return file_path

    def test_format_size(self):
        """Test size formatting function"""
        self.assertEqual(format_size(500), "500.00 B")
        self.assertEqual(format_size(1024), "1.00 KB")
        self.assertEqual(format_size(1024 * 1024), "1.00 MB")
        self.assertEqual(format_size(1024 * 1024 * 1024), "1.00 GB")

    def test_get_file_info(self):
        """Test file information retrieval"""
        test_file = self.create_test_file(b'Test content')
        info = get_file_info(test_file)

        self.assertIn("File Information:", info)
        self.assertIn(str(test_file), info)
        self.assertIn("Size:", info)
        self.assertIn("Last modified:", info)

    def test_process_file_compression(self):
        """Test file compression process"""
        # Create test file with repeating content
        test_content = b'A' * 1000
        input_file = self.create_test_file(test_content)
        output_file = Path(self.temp_dir) / "compressed.rle"

        # Test compression
        success = process_file(self.compressor, input_file, output_file, 'compress')
        self.assertTrue(success)
        self.assertTrue(output_file.exists())

        # Verify compressed file is smaller
        self.assertLess(output_file.stat().st_size, input_file.stat().st_size)

    def test_process_file_decompression(self):
        """Test file decompression process"""
        # Create and compress test file
        test_content = b'B' * 1000
        input_file = self.create_test_file(test_content)
        compressed_file = Path(self.temp_dir) / "compressed.rle"
        decompressed_file = Path(self.temp_dir) / "decompressed.txt"

        # Compress first
        process_file(self.compressor, input_file, compressed_file, 'compress')

        # Test decompression
        success = process_file(self.compressor, compressed_file, decompressed_file, 'decompress')
        self.assertTrue(success)
        self.assertTrue(decompressed_file.exists())

        # Verify content matches original
        with open(decompressed_file, 'rb') as f:
            decompressed_content = f.read()
        self.assertEqual(decompressed_content, test_content)

    def test_process_file_error_handling(self):
        """Test error handling in file processing"""
        # Test with non-existent input file
        input_file = Path(self.temp_dir) / "nonexistent.txt"
        output_file = Path(self.temp_dir) / "output.rle"

        success = process_file(self.compressor, input_file, output_file, 'compress')
        self.assertFalse(success)


if __name__ == '__main__':
    unittest.main()
