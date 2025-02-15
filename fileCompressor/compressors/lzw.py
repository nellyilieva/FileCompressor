import time
from pathlib import Path
from core.interfaces.compressor import BaseCompressor
from utils.bit_handler import BitHandler
from utils.progress_tracker import ProgressTracker
from utils.file_handler import FileHandler


class LZWCompressor(BaseCompressor):
    def __init__(self):
        self.stats = {
            'original_size': 0,
            'compressed_size': 0,
            'decompressed_size': 0,
            'compression_ratio': 0,
            'time_taken': 0
        }
        self.max_dict_size = 65536  # 16-bit codes

    def _initialize_dictionary(self):
        return {bytes([i]): i for i in range(256)}

    def _initialize_reverse_dictionary(self):
        return {i: bytes([i]) for i in range(256)}

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

        dictionary = self._initialize_dictionary()
        next_code = 256
        current_phrase = b''
        compressed_data = []
        bytes_processed = 0

        with FileHandler() as fh:
            fh.open_file(input_file, 'rb')
            while True:
                byte = fh.read_chunk(1)
                if not byte:
                    if current_phrase:
                        compressed_data.append(dictionary[current_phrase])
                    break

                phrase_plus_byte = current_phrase + byte
                if phrase_plus_byte in dictionary:
                    current_phrase = phrase_plus_byte
                else:
                    compressed_data.append(dictionary[current_phrase])
                    if next_code < self.max_dict_size:
                        dictionary[phrase_plus_byte] = next_code
                        next_code += 1
                    current_phrase = byte

                bytes_processed += 1
                if tracker:
                    tracker.update(bytes_processed)

        with FileHandler() as fh:
            fh.open_file(output_file, 'wb')
            fh.write_chunk(len(compressed_data).to_bytes(4, 'big'))
            for code in compressed_data:
                fh.write_chunk(code.to_bytes(2, 'big'))

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

        dictionary = self._initialize_reverse_dictionary()
        next_code = 256
        decompressed_data = bytearray()
        bytes_processed = 0

        with FileHandler() as fh:
            fh.open_file(input_file, 'rb')
            try:
                num_codes = int.from_bytes(fh.read_chunk(4), 'big')
                bytes_processed += 4

                if num_codes > 0:
                    code = int.from_bytes(fh.read_chunk(2), 'big')
                    bytes_processed += 2
                    decompressed_data.extend(dictionary[code])
                    old_code = code

                    for i in range(num_codes - 1):
                        code = int.from_bytes(fh.read_chunk(2), 'big')
                        bytes_processed += 2

                        if code in dictionary:
                            entry = dictionary[code]
                        elif code == next_code:
                            entry = dictionary[old_code] + dictionary[old_code][:1]
                        else:
                            raise ValueError(f"Invalid code: {code}")

                        decompressed_data.extend(entry)

                        if next_code < self.max_dict_size:
                            dictionary[next_code] = dictionary[old_code] + entry[:1]
                            next_code += 1

                        old_code = code

                        if tracker:
                            tracker.update(bytes_processed)

            except Exception as e:
                raise ValueError(f"Error during decompression: {str(e)}")

        with FileHandler() as fh:
            fh.open_file(output_file, 'wb')
            fh.write_chunk(decompressed_data)

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
