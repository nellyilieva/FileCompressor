import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import io
from contextlib import redirect_stdout, redirect_stderr
from utils.progress_tracker import ProgressStats, ProgressTracker
from ui.cli.command_line import CommandLineUI
from datetime import datetime


class TestCommandLineUI(unittest.TestCase):
    def setUp(self):
        self.cli = CommandLineUI()
        self.cli.engine = Mock()
        self.cli.engine.available_algorithms = ['rle', 'lzw']

        self.mock_compressor = Mock()
        self.mock_compressor.compress.return_value = {
            "original_size": 1000,
            "compressed_size": 500,
            "compression_ratio": 50.0,
            "time_taken": 1.5
        }
        self.mock_compressor.decompress.return_value = {
            "original_size": 500,
            "decompressed_size": 1000,
            "compression_ratio": 50.0,
            "time_taken": 1.5
        }
        self.cli.engine.get_compressor.return_value = self.mock_compressor

    def capture_output(self, func, *args, **kwargs):
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            func(*args, **kwargs)
        return out.getvalue().strip(), err.getvalue().strip()

    def test_show_error(self):
        out, err = self.capture_output(self.cli.show_error, "Test error")
        self.assertEqual(err, "Error: Test error")

    def test_progress_callback(self):
        stats = ProgressStats(
            bytes_processed=500,
            total_bytes=1000,
            start_time=time.time() - 1,
            current_time=time.time()
        )

        out, err = self.capture_output(self.cli._progress_callback, stats)

        self.assertIn("50.0%", out)
        self.assertIn("500/1000", out)
        self.assertIn("bytes/sec", out)
        self.assertIn("Remaining:", out)

    def test_show_stats(self):
        stats = {
            "original_size": 1000,
            "compressed_size": 500,
            "compression_ratio": 50.0,
            "time_taken": 1.5
        }
        out, err = self.capture_output(self.cli.show_stats, stats)
        self.assertIn("Original Size: 1000.00 B", out)
        self.assertIn("Compressed Size: 500.00 B", out)
        self.assertIn("Compression Ratio: 50.00%", out)
        self.assertIn("Time Taken: 1.50 seconds", out)

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

    @patch("builtins.input", side_effect=["cf nonexistent.txt output.txt", "exit"])
    @patch("sys.exit", side_effect=SystemExit)
    def test_handle_compression_file_not_found(self, mock_exit, mock_input):
        with self.assertRaises(SystemExit):
            out, err = self.capture_output(self.cli.start)
            self.assertIn("File not found", err)

    @patch("builtins.input", side_effect=["dcf nonexistent.txt output.txt", "exit"])
    @patch("sys.exit", side_effect=SystemExit)
    def test_handle_decompression_file_not_found(self, mock_exit, mock_input):
        with self.assertRaises(SystemExit):
            out, err = self.capture_output(self.cli.start)
            self.assertIn("File not found", err)

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.stat")
    @patch("builtins.input", side_effect=["rle", "cf test.txt test.compressed", "exit"])
    @patch("sys.exit", side_effect=SystemExit)
    def test_process_file_compression(self, mock_exit, mock_input, mock_stat, mock_exists):
        stat_result = MagicMock()
        stat_result.st_size = 1000
        mock_stat.return_value = stat_result

        with patch.object(self.cli, 'process_file', wraps=self.cli.process_file) as mock_process:
            with self.assertRaises(SystemExit):
                self.cli.start()

            self.assertEqual(self.cli.current_compressor, 'rle')

            mock_process.assert_called_with(
                'compress',
                Path("test.txt"),
                Path("test.rle"),
                'rle'
            )

    def test_process_file_invalid_operation(self):
        with self.assertRaises(ValueError):
            self.cli.process_file("invalid", Path("input.txt"), Path("output.txt"), None)

    def test_get_compressed_file_extension(self):
        self.cli.current_compressor = 'rle'
        self.assertEqual(self.cli._get_compressed_file_extension(), '.rle')

        self.cli.current_compressor = 'lzw'
        self.assertEqual(self.cli._get_compressed_file_extension(), '.lzw')

        self.cli.current_compressor = None
        self.assertEqual(self.cli._get_compressed_file_extension(), '.compressed')

    @patch("builtins.input", side_effect=["rle", "exit"])
    @patch("sys.exit", side_effect=SystemExit)
    def test_select_algorithm_rle(self, mock_exit, mock_input):
        with self.assertRaises(SystemExit):
            out, err = self.capture_output(self.cli.start)
        self.assertEqual(self.cli.current_compressor, 'rle')

    @patch("builtins.input", side_effect=["lzw", "exit"])
    @patch("sys.exit", side_effect=SystemExit)
    def test_select_algorithm_lzw(self, mock_exit, mock_input):
        with self.assertRaises(SystemExit):
            out, err = self.capture_output(self.cli.start)
        self.assertEqual(self.cli.current_compressor, 'lzw')

    @patch("builtins.input", side_effect=["stat test.txt", "exit"])
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.stat")
    @patch("sys.exit", side_effect=SystemExit)
    def test_display_file_info(self, mock_exit, mock_stat, mock_exists, mock_input):
        stat_result = MagicMock()
        stat_result.st_size = 1024
        stat_result.st_mtime = 1234567890
        mock_stat.return_value = stat_result

        datetime_mock = Mock()
        datetime_mock.strftime.return_value = "2009-02-14 01:31:30"

        with patch('datetime.datetime', spec=datetime) as mock_datetime:
            mock_datetime.fromtimestamp.return_value = datetime_mock

            with self.assertRaises(SystemExit):
                out, err = self.capture_output(self.cli.start)

                self.assertIn("File Information for: test.txt", out)
                self.assertIn("1.00 KB", out)
                self.assertIn(".txt", out)
                self.assertIn("2009-02-14 01:31:30", out)

    @patch("sys.exit", side_effect=SystemExit)
    @patch("builtins.input", side_effect=["exit"])
    def test_start_exit(self, mock_input, mock_exit):
        with self.assertRaises(SystemExit):
            self.cli.start()
        mock_exit.assert_called_once_with(0)


if __name__ == "__main__":
    unittest.main()
