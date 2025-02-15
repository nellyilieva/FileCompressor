from abc import ABC, abstractmethod
from pathlib import Path


class BaseCompressor(ABC):
    @abstractmethod
    def compress(self, input_file: Path, output_file: Path, tracker):
        pass

    @abstractmethod
    def decompress(self, input_file: Path, output_file: Path, tracker):
        pass

    @abstractmethod
    def get_compression_stats(self):
        pass
