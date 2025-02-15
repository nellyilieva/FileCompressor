import time
from pathlib import Path
from core.interfaces.compressor import BaseCompressor
from utils.bit_handler import BitHandler
from utils.progress_tracker import ProgressTracker
from utils.file_handler import FileHandler


class RLECompressor(BaseCompressor):
    def __init__(self):
        self.stats = {
            'original_size': 0,
            'compressed_size': 0,
            'compression_ratio': 0,
            'time_taken': 0
        }

    def compress(self, input_file: Path, output_file: Path, tracker):
        start_time = time.time()

        if input_file.stat().st_size == 0:
            with FileHandler() as fh:
                fh.open_file(output_file, 'wb')
                fh.write_chunk(b'')
            self.stats = {
                'original_size': 0,
                'compressed_size': 0,
                'compression_ratio': 0,
                'time_taken': time.time() - start_time
            }
            return self.stats

        bit_handler = BitHandler()
        bytes_processed = 0

        with FileHandler() as fh:
            fh.open_file(input_file, 'rb')
            with FileHandler() as fh_out:
                fh_out.open_file(output_file, 'wb')
                prev_byte = None
                count = 0

                while True:
                    byte = fh.read_chunk(1)
                    if not byte:
                        break

                    bytes_processed += 1
                    if tracker:
                        tracker.update(bytes_processed)

                    if byte == prev_byte:
                        count += 1
                        if count == 255:
                            fh_out.write_chunk(bit_handler.write_byte(count))
                            fh_out.write_chunk(bit_handler.write_byte(ord(prev_byte)))
                            count = 0
                    else:
                        if prev_byte is not None:
                            fh_out.write_chunk(bit_handler.write_byte(count))
                            fh_out.write_chunk(bit_handler.write_byte(ord(prev_byte)))
                        prev_byte = byte
                        count = 1

                if prev_byte is not None:
                    fh_out.write_chunk(bit_handler.write_byte(count))
                    fh_out.write_chunk(bit_handler.write_byte(ord(prev_byte)))

                final_bits = bit_handler.flush_bits()
                if final_bits:
                    fh_out.write_chunk(final_bits)

        original_size = input_file.stat().st_size
        compressed_size = output_file.stat().st_size
        compression_ratio = max(0, (1 - (compressed_size / original_size)) * 100)

        self.stats = {
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compression_ratio,
            'time_taken': time.time() - start_time
        }

        return self.stats

    def decompress(self, input_file: Path, output_file: Path, tracker):
        start_time = time.time()

        if input_file.stat().st_size == 0:
            with FileHandler() as fh:
                fh.open_file(output_file, 'wb')
                fh.write_chunk(b'')
            self.stats = {
                'original_size': 0,
                'compressed_size': 0,
                'decompressed_size': 0,
                'compression_ratio': 0,
                'time_taken': time.time() - start_time
            }
            return self.stats

        bytes_processed = 0
        with FileHandler() as fh:
            fh.open_file(input_file, 'rb')
            decompressed_data = bytearray()

            try:
                while True:
                    count_chunk = fh.read_chunk(1)
                    if not count_chunk:
                        break

                    byte_chunk = fh.read_chunk(1)
                    if not byte_chunk:
                        raise ValueError("Invalid compressed data: missing byte after count")

                    bytes_processed += 2

                    count = int.from_bytes(count_chunk, byteorder='big')
                    byte = int.from_bytes(byte_chunk, byteorder='big')

                    if count < 1 or count > 255:
                        raise ValueError("Invalid compressed data: count out of range")
                    if byte < 0 or byte > 255:
                        raise ValueError("Invalid compressed data: byte out of range")

                    decompressed_data.extend([byte] * count)

            except Exception as e:
                raise ValueError(f"Invalid compressed data: {str(e)}")

        with FileHandler() as fh_out:
            fh_out.open_file(output_file, 'wb')
            fh_out.write_chunk(decompressed_data)

        original_size = input_file.stat().st_size
        decompressed_size = len(decompressed_data)
        compression_ratio = max(0, (1 - (original_size / decompressed_size)) * 100) if decompressed_size > 0 else 0

        self.stats = {
            'original_size': original_size,
            'compressed_size': original_size,
            'decompressed_size': decompressed_size,
            'compression_ratio': compression_ratio,
            'time_taken': time.time() - start_time
        }
        return self.stats

    def get_compression_stats(self):
        return self.stats.copy()
