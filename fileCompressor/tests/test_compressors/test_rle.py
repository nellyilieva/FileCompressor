import unittest
from pathlib import Path
import os
from compressors.rle import RLECompressor


class TestRLECompressor(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_files")
        self.test_dir.mkdir(exist_ok=True)
        self.rle_compressor = RLECompressor()

    def tearDown(self):
        for file in self.test_dir.iterdir():
            file.unlink()
        self.test_dir.rmdir()

    def create_test_file(self, filename, content: bytes):
        file_path = self.test_dir / filename
        with open(file_path, 'wb') as f:
            f.write(content)
        return file_path

    def test_compress_decompress_simple(self):
        input_file = self.create_test_file("input.txt", b'AAAAABBBCC')
        compressed_file = self.test_dir / "compressed.rle"
        output_file = self.test_dir / "output.txt"

        self.rle_compressor.compress(input_file, compressed_file, None)
        self.rle_compressor.decompress(compressed_file, output_file, None)

        with open(output_file, 'rb') as f:
            result = f.read()
        self.assertEqual(result, b'AAAAABBBCC')

    def test_compress_decompress_no_repetition(self):
        input_file = self.create_test_file("input.txt", bytes(range(50)))
        compressed_file = self.test_dir / "compressed.rle"
        output_file = self.test_dir / "output.txt"

        self.rle_compressor.compress(input_file, compressed_file, None)
        self.rle_compressor.decompress(compressed_file, output_file, None)

        with open(output_file, 'rb') as f:
            result = f.read()
        self.assertEqual(result, bytes(range(50)))

    def test_compress_decompress_long_repetition(self):
        test_data = b'A' * 1000 + b'B' * 500
        input_file = self.create_test_file("input.txt", test_data)
        compressed_file = self.test_dir / "compressed.rle"
        output_file = self.test_dir / "output.txt"

        self.rle_compressor.compress(input_file, compressed_file, None)
        self.rle_compressor.decompress(compressed_file, output_file, None)

        with open(output_file, 'rb') as f:
            result = f.read()
        self.assertEqual(result, test_data)

    def test_empty_file(self):
        input_file = self.create_test_file("input.txt", b'')
        compressed_file = self.test_dir / "compressed.rle"
        output_file = self.test_dir / "output.txt"

        self.rle_compressor.compress(input_file, compressed_file, None)
        self.rle_compressor.decompress(compressed_file, output_file, None)

        self.assertEqual(output_file.stat().st_size, 0)

    def test_invalid_compressed_data(self):
        input_file = self.create_test_file("invalid.rle", b'\x01A\x02BInvalid')
        output_file = self.test_dir / "output.txt"

        with self.assertRaises(ValueError) as context:
            self.rle_compressor.decompress(input_file, output_file, None)

        self.assertIn("Invalid compressed data", str(context.exception))

    def test_compression_performance(self):
        patterns = {
            'repeated': b'A' * 10000,
            'alternating': b'AB' * 5000,
            'random': os.urandom(10000)
        }

        for pattern_name, data in patterns.items():
            with self.subTest(pattern=pattern_name):
                input_file = self.create_test_file(f"input_{pattern_name}.txt", data)
                compressed_file = self.test_dir / f"compressed_{pattern_name}.rle"
                output_file = self.test_dir / f"output_{pattern_name}.txt"

                self.rle_compressor.compress(input_file, compressed_file, None)
                self.rle_compressor.decompress(compressed_file, output_file, None)

                with open(output_file, 'rb') as f:
                    result = f.read()
                self.assertEqual(result, data)


if __name__ == '__main__':
    unittest.main()
