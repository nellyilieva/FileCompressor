from pathlib import Path
import time
from core.interfaces.compressor import BaseCompressor
from utils.bit_handler import BitHandler
from utils.progress_tracker import ProgressTracker


class RLECompressor(BaseCompressor):
    """Run-Length Encoding compression implementation"""

    def __init__(self):
        self._bit_handler = BitHandler()
        self._stats = {}
        self._current_progress = None

    def compress(self, input_file: Path, output_file: Path) -> None:
        """
        Compress a file using RLE compression

        Args:
            input_file: Path to input file
            output_file: Path to output file
        """
        start_time = time.time()
        input_size = input_file.stat().st_size

        # Handle empty file case
        if input_size == 0:
            with open(output_file, 'wb') as out_file:
                # Write original file size (0) for decompression
                out_file.write((0).to_bytes(8, byteorder='big'))

            end_time = time.time()
            self._stats = {
                'original_size': 0,
                'compressed_size': 8,  # Size of the file size header
                'compression_ratio': 0,
                'time_taken': end_time - start_time
            }
            return

        self._current_progress = ProgressTracker(max(1, input_size))

        with open(input_file, 'rb') as in_file, open(output_file, 'wb') as out_file:
            # Write original file size for decompression
            out_file.write(input_size.to_bytes(8, byteorder='big'))

            # Process file in chunks
            chunk_size = 8192  # 8KB chunks
            bytes_processed = 0
            current_byte = None
            run_length = 0

            while True:
                chunk = in_file.read(chunk_size)
                if not chunk:
                    break

                # Process each byte in the chunk
                for byte in chunk:
                    if current_byte is None:
                        current_byte = byte
                        run_length = 1
                        continue

                    if byte == current_byte and run_length < 255:
                        run_length += 1
                    else:
                        # Write the run
                        out_file.write(bytes([run_length, current_byte]))
                        current_byte = byte
                        run_length = 1

                bytes_processed += len(chunk)
                self._current_progress.update(bytes_processed)

            # Write final run if any
            if current_byte is not None:
                out_file.write(bytes([run_length, current_byte]))

        # Update compression statistics
        end_time = time.time()
        compressed_size = output_file.stat().st_size

        self._stats = {
            'original_size': input_size,
            'compressed_size': compressed_size,
            'compression_ratio': input_size / compressed_size if compressed_size > 0 else 0,
            'time_taken': end_time - start_time
        }

    def decompress(self, input_file: Path, output_file: Path) -> None:
        """
        Decompress an RLE compressed file

        Args:
            input_file: Path to compressed file
            output_file: Path to output file
        """
        start_time = time.time()

        with open(input_file, 'rb') as in_file, open(output_file, 'wb') as out_file:
            # Read original file size
            original_size = int.from_bytes(in_file.read(8), byteorder='big')

            # Handle empty file case
            if original_size == 0:
                end_time = time.time()
                self._stats = {
                    'original_size': 0,
                    'compressed_size': input_file.stat().st_size,
                    'compression_ratio': 0,
                    'time_taken': end_time - start_time
                }
                return

            self._current_progress = ProgressTracker(max(1, original_size))

            bytes_written = 0

            # Read runs until we reach original size
            while bytes_written < original_size:
                # Read run length and value
                run_data = in_file.read(2)
                if not run_data or len(run_data) != 2:
                    raise ValueError("Invalid compressed data")

                run_length, value = run_data

                # Write repeated value
                out_file.write(bytes([value] * run_length))
                bytes_written += run_length
                self._current_progress.update(bytes_written)

        # Update statistics
        end_time = time.time()
        self._stats = {
            'original_size': original_size,
            'compressed_size': input_file.stat().st_size,
            'compression_ratio': original_size / input_file.stat().st_size if input_file.stat().st_size > 0 else 0,
            'time_taken': end_time - start_time
        }

    def get_compression_stats(self):
        """Get statistics about the last compression/decompression operation"""
        return self._stats.copy()
