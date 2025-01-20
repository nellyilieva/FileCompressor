from abc import ABC, abstractmethod
from pathlib import Path


class BaseUI(ABC):

    @abstractmethod
    def start(self) -> None:
        """Start the user interface"""
        pass

    @abstractmethod
    def process_file(self, operation: str, input_file: Path, output_file: Path, algorithm):
        """
        Process a file with the specified operation and algorithm

        Args:
            operation (str): Either 'compress' or 'decompress'
            input_file (Path): Path to input file
            output_file (Path): Path to output file
            algorithm (Optional[str]): Compression algorithm to use - optional parameter
        """
        pass

    @abstractmethod
    def update_progress(self, progress: float, status: str):
        """
        Update operation progress

        Args:
            progress (float): Progress percentage (0-100)
            status (str): Current status message
        """
        pass

    @abstractmethod
    def show_error(self, message: str):
        """Display error message to user"""
        pass

    @abstractmethod
    def show_stats(self, stats: dict):
        """Display compression/decompression statistics"""
        pass
