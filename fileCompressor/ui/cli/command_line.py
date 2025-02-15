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

    def _print_menu(self):
        print("\nFile Compression Tool")
        print("1. Compress file")
        print("2. Decompress file")
        print("3. File information")
        print("4. Choose algorithm")
        print("5. Exit")

    def start(self):
        while True:
            self._print_menu()
            choice = input("Enter your choice (1-5): ").strip()

            if choice == '1':
                self._handle_compression()
            elif choice == '2':
                self._handle_decompression()
            elif choice == '3':
                self._display_file_info()
            elif choice == '4':
                self._select_algorithm()
            elif choice == '5':
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")

    def _select_algorithm(self):
        print("\nAvailable compression algorithms:")
        for i, algo in enumerate(self.engine.available_algorithms, 1):
            print(f"{i}. {algo.upper()}")

        choice = input("Select algorithm (or leave blank for auto-select): ").strip()
        if choice:
            try:
                algo_index = int(choice) - 1
                if 0 <= algo_index < len(self.engine.available_algorithms):
                    self.current_compressor = self.engine.available_algorithms[algo_index]
                    print(f"Selected algorithm: {self.current_compressor.upper()}")
                else:
                    print("Invalid selection")
            except ValueError:
                print("Invalid input")
        else:
            self.current_compressor = None
            print("Algorithm selection set to auto")

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

    def _handle_compression(self):
        input_path = input("Enter the path of the file to compress: ").strip()
        output_path = input("Enter the path for the compressed file: ").strip()

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

    def _handle_decompression(self):
        input_path = input("Enter the path of the file to decompress: ").strip()
        output_path = input("Enter the path for the decompressed file: ").strip()

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

    def _display_file_info(self):
        file_path = input("Enter the path of the file: ").strip()
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

    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
