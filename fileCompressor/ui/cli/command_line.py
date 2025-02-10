from pathlib import Path
import sys
from core.interfaces.ui import BaseUI
from compressors.rle import RLECompressor


class CommandLineUI(BaseUI):
    def __init__(self):
        self.compressor = RLECompressor()

    def start(self) -> None:
        while True:
            self._print_menu()
            choice = input("Enter your choice (1-4): ").strip()

            if choice == '1':
                self._handle_compression()
            elif choice == '2':
                self._handle_decompression()
            elif choice == '3':
                self._display_file_info()
            elif choice == '4':
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")

    def process_file(self, operation: str, input_file: Path, output_file: Path, algorithm=None):
        if operation not in ['compress', 'decompress']:
            self.show_error(f"Invalid operation: {operation}")
            raise ValueError(f"Invalid operation: {operation}")

        try:
            if operation == 'compress':
                self.compressor.compress(input_file, output_file)
            else:  # operation == 'decompress'
                self.compressor.decompress(input_file, output_file)
        except Exception as e:
            self.show_error(str(e))
            raise

    def update_progress(self, progress: float, status: str):
        bar_width = 50
        filled = int(bar_width * progress / 100)
        bar = '=' * filled + '-' * (bar_width - filled)
        print(f'\rProgress: [{bar}] {progress:.1f}% {status}', end='')
        if progress >= 100:
            print()

    def show_error(self, message: str):
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

    def _print_menu(self):
        print("\nFile Compression Tool")
        print("1. Compress file")
        print("2. Decompress file")
        print("3. File information")
        print("4. Exit")

    def _handle_compression(self):
        input_path = input("Enter the path of the file to compress: ").strip()
        output_path = input("Enter the path for the compressed file: ").strip()

        input_file = Path(input_path)
        output_file = Path(output_path)

        if not input_file.exists():
            self.show_error(f"File not found: {input_path}")
            return

        try:
            self.process_file('compress', input_file, output_file)
            stats = self.compressor.get_compression_stats()
            if stats:  # Only show stats if we got valid statistics
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
            self.process_file('decompress', input_file, output_file)
            stats = self.compressor.get_compression_stats()
            if stats:  # Only show stats if we got valid statistics
                self.show_stats(stats)
        except Exception as e:
            self.show_error(f"Decompression failed: {str(e)}")

    def _display_file_info(self):
        file_path = input("Enter the path of the file: ").strip()
        path = Path(file_path)

        if not path.exists():
            self.show_error(f"File not found: {file_path}")
            return

        print(f"\nFile Information for: {path.name}")
        print(f"Size: {self._format_size(path.stat().st_size)}")
        print(f"Extension: {path.suffix or 'None'}")
        print(f"Last modified: {path.stat().st_mtime}")

    def _format_size(self, size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
