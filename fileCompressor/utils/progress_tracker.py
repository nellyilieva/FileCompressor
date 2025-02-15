import time
from typing import Optional, Callable
from dataclasses import dataclass


@dataclass
class ProgressStats:
    bytes_processed: int = 0
    total_bytes: int = 0
    start_time: float = 0.0
    current_time: float = 0.0

    @property
    def elapsed_time(self):
        return self.current_time - self.start_time

    @property
    def progress_percentage(self):
        if self.total_bytes == 0:
            return 0.0
        return (self.bytes_processed / self.total_bytes) * 100

    @property
    def processing_speed(self):
        if self.elapsed_time == 0:
            return 0.0
        return self.bytes_processed / self.elapsed_time

    @property
    def estimated_time_remaining(self):
        if self.processing_speed == 0:
            return float('inf')
        remaining_bytes = self.total_bytes - self.bytes_processed
        return remaining_bytes / self.processing_speed


class ProgressTracker:
    def __init__(self, total_bytes, callback: Optional[Callable] = None):
        if total_bytes <= 0:
            raise ValueError("Total bytes must be positive")

        self._stats = ProgressStats(
            total_bytes=total_bytes,
            start_time=time.time(),
            current_time=time.time()
        )
        self._callback = callback

    @property
    def stats(self):
        return self._stats

    def update(self, bytes_processed):
        if bytes_processed < 0:
            raise ValueError("Bytes processed cannot be negative")
        if bytes_processed > self._stats.total_bytes:
            raise ValueError("Bytes processed cannot exceed total bytes")

        self._stats.bytes_processed = bytes_processed
        self._stats.current_time = time.time()

        if self._callback:
            self._callback(self._stats)

    def format_progress(self):
        stats = self.stats
        return (
            f"Progress: {stats.progress_percentage:.1f}% "
            f"({stats.bytes_processed}/{stats.total_bytes} bytes) | "
            f"Speed: {stats.processing_speed:.1f} bytes/sec | "
            f"Remaining: {stats.estimated_time_remaining:.1f} sec"
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
