from pathlib import Path
from compressors.rle import RLECompressor
from compressors.lzw import LZWCompressor


class CompressionEngine:
    def __init__(self):
        self._algorithms = {
            'rle': RLECompressor,
            'lzw': LZWCompressor
        }

    @property
    def available_algorithms(self):
        return list(self._algorithms.keys())

    def get_compressor(self, file_path: Path, algorithm):
        if algorithm:
            if algorithm not in self._algorithms:
                raise ValueError(f"Unknown compression algorithm: {algorithm}")
            return self._algorithms[algorithm]()

        file_size = file_path.stat().st_size
        return self._algorithms['lzw']() if file_size > 1024 * 1024 else self._algorithms['rle']()
