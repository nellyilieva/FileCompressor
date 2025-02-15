from abc import ABC, abstractmethod
from pathlib import Path


class BaseUI(ABC):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def process_file(self, operation: str, input_file: Path, output_file: Path, algorithm):
        pass

    @abstractmethod
    def update_progress(self, progress: float, status: str):
        pass

    @abstractmethod
    def show_error(self, message: str):
        pass

    @abstractmethod
    def show_stats(self, stats: dict):
        pass
