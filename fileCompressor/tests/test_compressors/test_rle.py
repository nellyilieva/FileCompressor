import unittest
import tempfile
from pathlib import Path
import os
import shutil
from compressors.rle import RLECompressor


class TestRLECompressor(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.rle_compressor = RLECompressor()

    def tearDown(self):
        """Clean up after each test method"""
        shutil.rmtree(self.temp_dir)

    def create_test_file(self, filename: str, content: bytes) -> Path:
        """Helper to create test file with specific content"""
        file_path = Path(self.temp_dir) / filename
        with open(file_path, 'wb') as f:
            f.write(content)
        return file_path

    def test_compress_decompress_simple(self):
        """Test basic compression and decompression with simple repeated data"""
        # Create test file with simple repeated content
        input_file = self.create_test_file("input.txt", b'AAAAABBBCC')
        compressed_file = Path(self.temp_dir) / "compressed.rle"
        output_file = Path(self.temp_dir) / "output.txt"

        # Compress
        self.rle_compressor.compress(input_file, compressed_file)

        # Verify compression stats
        stats = self.rle_compressor.get_compression_stats()
        self.assertEqual(stats['original_size'], 10)  # len('AAAAABBBCC')
        self.assertGreater(stats['compressed_size'], 0)
        self.assertGreater(stats['time_taken'], 0)

        # Decompress
        self.rle_compressor.decompress(compressed_file, output_file)

        # Verify content matches
        with open(output_file, 'rb') as f:
            result = f.read()
        self.assertEqual(result, b'AAAAABBBCC')

    def test_compress_decompress_no_repetition(self):
        """Test compression with data that has no repetition"""
        input_file = self.create_test_file("input.txt", bytes(range(50)))
        compressed_file = Path(self.temp_dir) / "compressed.rle"
        output_file = Path(self.temp_dir) / "output.txt"

        # Compress and decompress
        self.rle_compressor.compress(input_file, compressed_file)
        self.rle_compressor.decompress(compressed_file, output_file)

        # Verify content matches
        with open(output_file, 'rb') as f:
            result = f.read()
        self.assertEqual(result, bytes(range(50)))

    def test_compress_decompress_long_repetition(self):
        """Test compression with long sequences of repeated data"""
        # Create data with runs longer than 255 (max run length)
        test_data = b'A' * 1000 + b'B' * 500
        input_file = self.create_test_file("input.txt", test_data)
        compressed_file = Path(self.temp_dir) / "compressed.rle"
        output_file = Path(self.temp_dir) / "output.txt"

        # Compress and decompress
        self.rle_compressor.compress(input_file, compressed_file)
        self.rle_compressor.decompress(compressed_file, output_file)

        # Verify content matches
        with open(output_file, 'rb') as f:
            result = f.read()
        self.assertEqual(result, test_data)

    def test_empty_file(self):
        """Test handling of empty files"""
        input_file = self.create_test_file("input.txt", b'')
        compressed_file = Path(self.temp_dir) / "compressed.rle"
        output_file = Path(self.temp_dir) / "output.txt"

        # Compress
        self.rle_compressor.compress(input_file, compressed_file)

        # Check compression stats for empty file
        stats = self.rle_compressor.get_compression_stats()
        self.assertEqual(stats['original_size'], 0)
        self.assertEqual(stats['compressed_size'], 8)  # Size of the file size header
        self.assertEqual(stats['compression_ratio'], 0)
        self.assertGreater(stats['time_taken'], 0.0)

        # Decompress
        self.rle_compressor.decompress(compressed_file, output_file)

        # Verify the decompressed file is empty
        self.assertEqual(output_file.stat().st_size, 0)

        # Check decompression stats
        stats = self.rle_compressor.get_compression_stats()
        self.assertEqual(stats['original_size'], 0)
        self.assertEqual(stats['compressed_size'], 8)
        self.assertEqual(stats['compression_ratio'], 0)
        self.assertGreater(stats['time_taken'], 0.0)

    def test_compression_progress(self):
        """Test progress tracking during compression"""
        # Create larger test file to better test progress
        test_data = b'A' * 100000 + b'B' * 100000
        input_file = self.create_test_file("input.txt", test_data)
        compressed_file = Path(self.temp_dir) / "compressed.rle"

        # Compress and check progress
        self.rle_compressor.compress(input_file, compressed_file)

        # Verify progress tracker reached 100%
        self.assertEqual(
            self.rle_compressor._current_progress.stats.progress_percentage,
            100.0
        )

    def test_invalid_compressed_data(self):
        """Test handling of invalid compressed data"""
        input_file = self.create_test_file("invalid.rle", b'Invalid RLE data')
        output_file = Path(self.temp_dir) / "output.txt"

        # Attempt to decompress should raise error
        with self.assertRaises(ValueError):
            self.rle_compressor.decompress(input_file, output_file)

    def test_compression_performance(self):
        """Test compression performance with various data patterns"""
        # Test with different patterns
        patterns = {
            'repeated': b'A' * 10000,
            'alternating': b'AB' * 5000,
            'random': bytes(os.urandom(10000))
        }

        for pattern_name, data in patterns.items():
            with self.subTest(pattern=pattern_name):
                input_file = self.create_test_file(f"input_{pattern_name}.txt", data)
                compressed_file = Path(self.temp_dir) / f"compressed_{pattern_name}.rle"
                output_file = Path(self.temp_dir) / f"output_{pattern_name}.txt"

                # Compress and decompress
                self.rle_compressor.compress(input_file, compressed_file)
                self.rle_compressor.decompress(compressed_file, output_file)

                # Verify content and check performance
                stats = self.rle_compressor.get_compression_stats()
                self.assertGreater(stats['time_taken'], 0)

                with open(output_file, 'rb') as f:
                    result = f.read()
                self.assertEqual(result, data)


if __name__ == '__main__':
    unittest.main()
