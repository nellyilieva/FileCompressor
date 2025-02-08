import os
from pathlib import Path


class FileHandler:
    # default chunk_size -> 8K
    def __init__(self, chunk_size: int = 8192):
        self.chunk_size = chunk_size
        self._current_file = None
        self._file_size = 0

    @property
    def chunk_size(self) -> int:
        """Get the current chunk size"""
        return self._chunk_size

    @chunk_size.setter
    def chunk_size(self, value: int) -> None:
        """Set the chunk size"""
        if value <= 0:
            raise ValueError("Chunk size must be positive")
        self._chunk_size = value

    @property
    def file_size(self) -> int:
        """Get the current file size"""
        return self._file_size

    @property
    def is_open(self) -> bool:
        """Check if a file is currently open"""
        return self._current_file is not None

    def open_file(self, file_path: Path, mode: str = 'rb'):
        self._current_file = open(file_path, mode)
        if mode == 'rb':
            self._file_size = os.path.getsize(file_path)

    def close_file(self):
        if self._current_file:
            self._current_file.close()
            self._current_file = None

    def read_chunks(self):
        if not self._current_file or self._current_file.mode != 'rb':
            raise IOError("File not open for reading")

        while True:
            chunk = self._current_file.read(self.chunk_size)
            if not chunk:
                break
            yield chunk

    def write_chunk(self, chunk: bytes) -> None:
        if not self._current_file or self._current_file.mode != 'wb':
            raise IOError("File not open for writing")

        self._current_file.write(chunk)

    def get_file_size(self) -> int:
        return self._file_size

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_file()
