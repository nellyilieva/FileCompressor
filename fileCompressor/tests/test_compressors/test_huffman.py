# import unittest
# from pathlib import Path
# import os
# from compressors.huffman import HuffmanCompressor
#
#
# class TestHuffmanCompressor(unittest.TestCase):
#     def setUp(self):
#         """Initialize a HuffmanCompressor instance for each test."""
#         self.compressor = HuffmanCompressor()
#         self.temp_dir = Path("test_temp")
#         self.temp_dir.mkdir(exist_ok=True)
#
#     def tearDown(self):
#         """Clean up temporary files after each test."""
#         for file in self.temp_dir.iterdir():
#             file.unlink()
#         self.temp_dir.rmdir()
#
#     def test_compress_decompress_empty_file(self):
#         """Test compressing and decompressing an empty file."""
#         input_file = self.temp_dir / "empty.txt"
#         output_file = self.temp_dir / "compressed.bin"
#         decompressed_file = self.temp_dir / "decompressed.txt"
#
#         # Create an empty file
#         with open(input_file, 'wb') as f:
#             pass
#
#         # Compress and decompress
#         self.compressor.compress(input_file, output_file)
#         self.compressor.decompress(output_file, decompressed_file)
#
#         # Verify decompressed file is empty
#         self.assertEqual(os.path.getsize(decompressed_file), 0)
#
#         # Verify stats
#         stats = self.compressor.get_compression_stats()
#         self.assertEqual(stats['original_size'], 0)
#         self.assertEqual(stats['compressed_size'], 0)
#         self.assertEqual(stats['compression_ratio'], 1.0)
#         self.assertGreaterEqual(stats['time_taken'], 0)
#
#     def test_compress_decompress_small_file(self):
#         """Test compressing and decompressing a small text file."""
#         input_file = self.temp_dir / "small.txt"
#         output_file = self.temp_dir / "compressed.bin"
#         decompressed_file = self.temp_dir / "decompressed.txt"
#
#         # Create a small file
#         with open(input_file, 'wb') as f:
#             f.write(b"hello world")
#
#         # Compress and decompress
#         self.compressor.compress(input_file, output_file)
#         self.compressor.decompress(output_file, decompressed_file)
#
#         # Verify decompressed file matches original
#         with open(input_file, 'rb') as f1, open(decompressed_file, 'rb') as f2:
#             self.assertEqual(f1.read(), f2.read())
#
#         # Verify stats
#         stats = self.compressor.get_compression_stats()
#         self.assertEqual(stats['original_size'], 11)
#         self.assertGreater(stats['compressed_size'], 0)
#         self.assertGreater(stats['compression_ratio'], 0)
#         self.assertGreaterEqual(stats['time_taken'], 0)
#
#     def test_compress_decompress_large_file(self):
#         """Test compressing and decompressing a large file."""
#         input_file = self.temp_dir / "large.txt"
#         output_file = self.temp_dir / "compressed.bin"
#         decompressed_file = self.temp_dir / "decompressed.txt"
#
#         # Create a large file (1MB of random data)
#         with open(input_file, 'wb') as f:
#             f.write(os.urandom(1024 * 1024))
#
#         # Compress and decompress
#         self.compressor.compress(input_file, output_file)
#         self.compressor.decompress(output_file, decompressed_file)
#
#         # Verify decompressed file matches original
#         with open(input_file, 'rb') as f1, open(decompressed_file, 'rb') as f2:
#             self.assertEqual(f1.read(), f2.read())
#
#         # Verify stats
#         stats = self.compressor.get_compression_stats()
#         self.assertEqual(stats['original_size'], 1024 * 1024)
#         self.assertGreater(stats['compressed_size'], 0)
#         self.assertGreater(stats['compression_ratio'], 0)
#         self.assertGreaterEqual(stats['time_taken'], 0)
#
#     def test_compression_stats(self):
#         """Test compression statistics for a small file."""
#         input_file = self.temp_dir / "test.txt"
#         output_file = self.temp_dir / "compressed.bin"
#
#         # Create a test file
#         with open(input_file, 'wb') as f:
#             f.write(b"test data")
#
#         # Compress and check stats
#         self.compressor.compress(input_file, output_file)
#         stats = self.compressor.get_compression_stats()
#
#         self.assertEqual(stats['original_size'], 9)
#         self.assertGreater(stats['compressed_size'], 0)
#         self.assertGreater(stats['compression_ratio'], 0)
#         self.assertGreaterEqual(stats['time_taken'], 0)
#
#     def test_progress_tracker_callback(self):
#         """Test progress tracking during compression."""
#         input_file = self.temp_dir / "progress_test.txt"
#         output_file = self.temp_dir / "compressed.bin"
#
#         # Create a test file
#         with open(input_file, 'wb') as f:
#             f.write(b"progress tracking test data")
#
#         # Compress and capture progress output
#         import io
#         from contextlib import redirect_stdout
#
#         f = io.StringIO()
#         with redirect_stdout(f):
#             self.compressor.compress(input_file, output_file)
#         output = f.getvalue()
#
#         # Verify progress output
#         self.assertIn("Progress:", output)
#         self.assertIn("Speed:", output)
#         self.assertIn("Remaining:", output)
#
#     def test_decompress_invalid_file(self):
#         """Test decompressing an invalid file."""
#         input_file = self.temp_dir / "invalid.bin"
#         output_file = self.temp_dir / "decompressed.txt"
#
#         # Create an invalid compressed file
#         with open(input_file, 'wb') as f:
#             f.write(b"invalid data")
#
#         # Attempt to decompress and verify exception
#         with self.assertRaises(ValueError, msg="Invalid Huffman tree data"):
#             self.compressor.decompress(input_file, output_file)
#
#     def test_compress_decompress_binary_file(self):
#         """Test compressing and decompressing a binary file."""
#         input_file = self.temp_dir / "binary.bin"
#         output_file = self.temp_dir / "compressed.bin"
#         decompressed_file = self.temp_dir / "decompressed.bin"
#
#         # Create a binary file with random data
#         with open(input_file, 'wb') as f:
#             f.write(os.urandom(512))  # 512 bytes of random data
#
#         # Compress and decompress
#         self.compressor.compress(input_file, output_file)
#         self.compressor.decompress(output_file, decompressed_file)
#
#         # Verify decompressed file matches original
#         with open(input_file, 'rb') as f1, open(decompressed_file, 'rb') as f2:
#             self.assertEqual(f1.read(), f2.read())
#
#     def test_compress_decompress_large_binary_file(self):
#         """Test compressing and decompressing a large binary file."""
#         input_file = self.temp_dir / "large_binary.bin"
#         output_file = self.temp_dir / "compressed.bin"
#         decompressed_file = self.temp_dir / "decompressed.bin"
#
#         # Create a large binary file (5MB of random data)
#         with open(input_file, 'wb') as f:
#             f.write(os.urandom(5 * 1024 * 1024))
#
#         # Compress and decompress
#         self.compressor.compress(input_file, output_file)
#         self.compressor.decompress(output_file, decompressed_file)
#
#         # Verify decompressed file matches original
#         with open(input_file, 'rb') as f1, open(decompressed_file, 'rb') as f2:
#             self.assertEqual(f1.read(), f2.read())
#
#
# if __name__ == '__main__':
#     unittest.main()
