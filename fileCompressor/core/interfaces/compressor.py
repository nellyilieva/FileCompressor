from abc import ABC, abstractmethod
from pathlib import Path


class BaseCompressor(ABC):
    @abstractmethod
    def compress(self, input_file: Path, output_file: Path):
        pass

    @abstractmethod
    def decompress(self, input_file: Path, output_file: Path):
        pass

    @abstractmethod
    def get_compression_stats(self):
        """
        Get statistics about the last compression/decompression operation
        Returns: dict: Dictionary containing statistics like:
                        - original_size: Size of original file in bytes
                        - compressed_size: Size of compressed file in bytes
                        - compression_ratio: Ratio of compression (original/compressed)
                        - time_taken: Time taken for the operation in seconds
        """
        pass
