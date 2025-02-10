import unittest
from pathlib import Path
from unittest.mock import Mock, patch
import io
import sys
from contextlib import contextmanager

from ui.cli.command_line import CommandLineUI


@contextmanager
def capture_output():
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestCommandLineUI(unittest.TestCase):
    def setUp(self):
        self.cli = CommandLineUI()
        self.mock_compressor = Mock()
        # Set up mock stats return value
        self.mock_stats = {
            'original_size': 1000,
            'compressed_size': 500,
            'compression_ratio': 50.0,
            'time_taken': 1.5
        }
        self.mock_compressor.get_compression_stats.return_value = self.mock_stats
        self.cli.compressor = self.mock_compressor

    def test_show_error(self):
        with capture_output() as (out, err):
            self.cli.show_error("Test error")
            self.assertEqual(err.getvalue().strip(), "Error: Test error")

    def test_update_progress(self):
        with capture_output() as (out, err):
            self.cli.update_progress(50.0, "Processing")
            self.assertIn("50.0%", out.getvalue())
            self.assertIn("Processing", out.getvalue())

    def test_show_stats(self):
        stats = {
            'original_size': 1000,
            'compressed_size': 500,
            'compression_ratio': 50.0,
            'time_taken': 1.5
        }
        with capture_output() as (out, err):
            self.cli.show_stats(stats)
            output = out.getvalue()
            self.assertIn("Original Size: 1000.00 B", output)
            self.assertIn("Compressed Size: 500.00 B", output)
            self.assertIn("Compression Ratio: 50.00%", output)
            self.assertIn("Time Taken: 1.50 seconds", output)

    @patch('builtins.input')
    def test_handle_compression_file_not_found(self, mock_input):
        mock_input.side_effect = ["nonexistent.txt", "output.txt"]
        with capture_output() as (out, err):
            self.cli._handle_compression()
            self.assertIn("File not found", err.getvalue())

    @patch('builtins.input')
    def test_handle_decompression_file_not_found(self, mock_input):
        mock_input.side_effect = ["nonexistent.txt", "output.txt"]
        with capture_output() as (out, err):
            self.cli._handle_decompression()
            self.assertIn("File not found", err.getvalue())

    def test_format_size(self):
        test_cases = [
            (500, "500.00 B"),
            (1024, "1.00 KB"),
            (1024 * 1024, "1.00 MB"),
            (1024 * 1024 * 1024, "1.00 GB"),
        ]
        for size, expected in test_cases:
            with self.subTest(size=size):
                self.assertEqual(self.cli._format_size(size), expected)

    @patch('pathlib.Path.exists')
    @patch('builtins.input')
    def test_process_file_compression(self, mock_input, mock_exists):
        # Setup
        mock_exists.return_value = True
        mock_input.side_effect = ["test.txt", "test.compressed"]

        # Execute
        self.cli._handle_compression()

        # Verify
        self.mock_compressor.compress.assert_called_once()
        self.mock_compressor.get_compression_stats.assert_called_once()

    def test_process_file_invalid_operation(self):
        with self.assertRaises(ValueError):
            self.cli.process_file("invalid", Path("input.txt"), Path("output.txt"))

    def test_show_stats_invalid_format(self):
        with capture_output() as (out, err):
            self.cli.show_stats(None)  # Test with invalid stats
            self.assertIn("Invalid statistics format", err.getvalue())


if __name__ == '__main__':
    unittest.main()
