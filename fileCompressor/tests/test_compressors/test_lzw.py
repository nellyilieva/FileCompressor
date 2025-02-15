import unittest
import os
from pathlib import Path
from compressors.lzw import LZWCompressor


class TestLZWCompressor(unittest.TestCase):
    def setUp(self):
        self.compressor = LZWCompressor()
        self.test_dir = Path(__file__).parent / "test_files"
        self.test_dir.mkdir(exist_ok=True)

        self.small_text_file = self.test_dir / "small.txt"
        self.large_text_file = self.test_dir / "large.txt"
        self.binary_file = self.test_dir / "binary.bin"

        self.small_text_file.write_text("a" * 100 + "b" * 50 + "c" * 25)

        with open(self.large_text_file, "wb") as f:
            f.write(os.urandom(1024 * 1024))

        with open(self.binary_file, "wb") as f:
            f.write(os.urandom(1024 * 100))

    def tearDown(self):
        for file in self.test_dir.glob("*"):
            file.unlink()
        self.test_dir.rmdir()

    def test_compress_decompress_small_text(self):
        compressed_file = self.test_dir / "small.lzw"
        decompressed_file = self.test_dir / "small_decompressed.txt"

        self.compressor.compress(self.small_text_file, compressed_file, None)
        self.compressor.decompress(compressed_file, decompressed_file, None)

        with open(self.small_text_file, "r") as original, open(decompressed_file, "r") as decompressed:
            self.assertEqual(original.read(), decompressed.read())

        stats = self.compressor.get_compression_stats()
        self.assertGreater(stats['original_size'], 0)
        self.assertGreater(stats['compressed_size'], 0)
        self.assertGreaterEqual(stats['compression_ratio'], 0)
        self.assertGreaterEqual(stats['time_taken'], 0)

    def test_compress_decompress_large_text(self):
        compressed_file = self.test_dir / "large.lzw"
        decompressed_file = self.test_dir / "large_decompressed.txt"

        self.compressor.compress(self.large_text_file, compressed_file, None)
        self.compressor.decompress(compressed_file, decompressed_file, None)

        with open(self.large_text_file, "rb") as original, open(decompressed_file, "rb") as decompressed:
            self.assertEqual(original.read(), decompressed.read())

    def test_compress_decompress_binary_data(self):
        compressed_file = self.test_dir / "binary.lzw"
        decompressed_file = self.test_dir / "binary_decompressed.bin"

        self.compressor.compress(self.binary_file, compressed_file, None)
        self.compressor.decompress(compressed_file, decompressed_file, None)

        with open(self.binary_file, "rb") as original, open(decompressed_file, "rb") as decompressed:
            self.assertEqual(original.read(), decompressed.read())

    def test_empty_file(self):
        empty_file = self.test_dir / "empty.txt"
        empty_file.touch()

        compressed_file = self.test_dir / "empty.lzw"
        decompressed_file = self.test_dir / "empty_decompressed.txt"

        self.compressor.compress(empty_file, compressed_file, None)
        self.compressor.decompress(compressed_file, decompressed_file, None)

        self.assertEqual(empty_file.stat().st_size, 0)
        self.assertEqual(decompressed_file.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
