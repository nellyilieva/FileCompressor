import os
from pathlib import Path


class FileHandler:
    def __init__(self, chunk_size=8192):
        self.chunk_size = chunk_size
        self._current_file = None
        self._file_size = 0

    @property
    def chunk_size(self):
        return self._chunk_size

    @chunk_size.setter
    def chunk_size(self, value):
        if value <= 0:
            raise ValueError("Chunk size must be positive")
        self._chunk_size = value

    @property
    def file_size(self):
        return self._file_size

    @property
    def is_open(self):
        return self._current_file is not None

    def open_file(self, file_path: Path, mode='rb'):
        if self.is_open:
            self.close_file()
        try:
            self._current_file = open(file_path, mode)
            if 'r' in mode:
                self._file_size = os.path.getsize(file_path)
        except Exception as e:
            raise IOError(f"Failed to open file: {str(e)}")

    def close_file(self):
        if self._current_file:
            try:
                self._current_file.close()
            except Exception as e:
                raise IOError(f"Failed to close file: {str(e)}")
            finally:
                self._current_file = None

    def read_chunk(self, size) -> bytes:
        if not self.is_open or 'r' not in self._current_file.mode:
            raise IOError("File not open for reading")
        if size is None:
            size = self.chunk_size
        try:
            return self._current_file.read(size)
        except Exception as e:
            raise IOError(f"Failed to read from file: {str(e)}")

    def write_chunk(self, chunk: bytes):
        if not self.is_open or 'w' not in self._current_file.mode:
            raise IOError("File not open for writing")
        try:
            self._current_file.write(chunk)
            self._current_file.flush()
        except Exception as e:
            raise IOError(f"Failed to write to file: {str(e)}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_file()
        if exc_type is not None:
            raise exc_val
