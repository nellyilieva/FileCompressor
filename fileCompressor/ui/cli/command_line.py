from pathlib import Path
import sys
from datetime import datetime
from core.interfaces.ui import BaseUI
from core.compression_engine import CompressionEngine
from utils.progress_tracker import ProgressStats, ProgressTracker


class CommandLineUI(BaseUI):
    def __init__(self):
        self.engine = CompressionEngine()
        self.current_compressor = None

    def start(self):
        print("File Compression Tool - Type 'help' for a list of commands.")
        while True:
            try:
                command = input("> ").strip().lower()
                if not command:
                    continue

                if command == 'help':
                    self._print_help()
                elif command.startswith('cf '):
                    self._handle_compression(command)
                elif command.startswith('dcf '):
                    self._handle_decompression(command)
                elif command == 'rle':
                    self._select_algorithm('rle')
                elif command == 'lzw':
                    self._select_algorithm('lzw')
                elif command.startswith('stat '):
                    self._display_file_info(command)
                elif command == 'exit':
                    sys.exit(0)
                else:
                    print("Invalid command. Type 'help' for a list of commands.")
            except Exception as e:
                self.show_error(str(e))

    def _print_help(self):
        print("\nAvailable commands:")
        print("  cf <input_file> <output_file> - Compress a file")
        print("  dcf <input_file> <output_file> - Decompress a file")
        print("  rle - Select Run-Length Encoding (RLE) algorithm")
        print("  lzw - Select Lempel-Ziv-Welch (LZW) algorithm")
        print("  stat <file_path> - Display file information")
        print("  exit - Exit the program")
        print("  help - Display this help message")

    def _select_algorithm(self, algorithm: str):
        if algorithm in self.engine.available_algorithms:
            self.current_compressor = algorithm
            print(f"Selected algorithm: {algorithm.upper()}")
        else:
            print(f"Invalid algorithm: {algorithm}")

    def _handle_compression(self, command: str):
        parts = command.split()
        if len(parts) != 3:
            self.show_error("Usage: cf <input_file> <output_file>")
            return

        input_path, output_path = parts[1], parts[2]
        input_file = Path(input_path)
        output_file = Path(output_path)

        if not input_file.exists():
            self.show_error(f"File not found: {input_path}")
            return

        extension = self._get_compressed_file_extension()
        output_file = output_file.with_suffix(extension)

        try:
            stats = self.process_file('compress', input_file, output_file, self.current_compressor)
            if stats:
                self.show_stats(stats)
        except Exception as e:
            self.show_error(f"Compression failed: {str(e)}")

    def _handle_decompression(self, command: str):
        parts = command.split()
        if len(parts) != 3:
            self.show_error("Usage: dcf <input_file> <output_file>")
            return

        input_path, output_path = parts[1], parts[2]
        input_file = Path(input_path)
        output_file = Path(output_path)

        if not input_file.exists():
            self.show_error(f"File not found: {input_path}")
            return

        try:
            stats = self.process_file('decompress', input_file, output_file, self.current_compressor)
            if stats:
                self.show_stats(stats)
        except Exception as e:
            self.show_error(f"Decompression failed: {str(e)}")

    def _display_file_info(self, command: str):
        parts = command.split()
        if len(parts) != 2:
            self.show_error("Usage: stat <file_path>")
            return

        file_path = parts[1]
        path = Path(file_path)

        if not path.exists():
            self.show_error(f"File not found: {file_path}")
            return

        last_modified_timestamp = path.stat().st_mtime
        last_modified_time = datetime.fromtimestamp(last_modified_timestamp).strftime('%Y-%m-%d %H:%M:%S')

        print(f"\nFile Information for: {path.name}")
        print(f"Size: {self._format_size(path.stat().st_size)}")
        print(f"Extension: {path.suffix or 'None'}")
        print(f"Last modified: {last_modified_time}")

    def _get_compressed_file_extension(self):
        if self.current_compressor:
            if self.current_compressor == 'rle':
                return '.rle'
            elif self.current_compressor == 'lzw':
                return '.lzw'
        else:
            return '.compressed'

    def _progress_callback(self, stats: ProgressStats):
        progress_str = (
            f"\rProgress: {stats.progress_percentage:.1f}% "
            f"({stats.bytes_processed}/{stats.total_bytes} bytes) | "
            f"Speed: {stats.processing_speed:.1f} bytes/sec | "
            f"Remaining: {stats.estimated_time_remaining:.1f} sec"
        )
        print(progress_str, end='')
        if stats.progress_percentage >= 100:
            print()

    def process_file(self, operation, input_file: Path, output_file: Path, algorithm):
        if operation not in ['compress', 'decompress']:
            self.show_error(f"Invalid operation: {operation}")
            raise ValueError(f"Invalid operation: {operation}")

        try:
            compressor = self.engine.get_compressor(input_file, algorithm)

            tracker = ProgressTracker(input_file.stat().st_size, self._progress_callback)

            if operation == 'compress':
                stats = compressor.compress(input_file, output_file, tracker)
            else:
                stats = compressor.decompress(input_file, output_file, tracker)

            return stats
        except Exception as e:
            self.show_error(str(e))
            raise

    def update_progress(self, progress, status):
        bar_width = 50
        filled = int(bar_width * progress / 100)
        bar = '=' * filled + '-' * (bar_width - filled)
        print(f'Progress: [{bar}] {progress:.1f}% {status}', end='')
        if progress >= 100:
            print()

    def show_error(self, message):
        print(f"Error: {message}", file=sys.stderr)

    def show_stats(self, stats):
        if not isinstance(stats, dict):
            self.show_error("Invalid statistics format")
            return

        print("\nOperation Statistics:")
        for key, value in stats.items():
            if isinstance(value, (int, float)):
                if 'size' in key:
                    print(f"{key.replace('_', ' ').title()}: {self._format_size(value)}")
                elif 'ratio' in key:
                    print(f"{key.replace('_', ' ').title()}: {value:.2f}%")
                elif 'time' in key:
                    print(f"{key.replace('_', ' ').title()}: {value:.2f} seconds")
                else:
                    print(f"{key.replace('_', ' ').title()}: {value}")

    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
