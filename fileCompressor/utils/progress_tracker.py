import time
from typing import Optional, Callable
from dataclasses import dataclass


@dataclass
class ProgressStats:
    """Statistics about the progress of an operation"""
    bytes_processed: int = 0
    total_bytes: int = 0
    start_time: float = 0.0
    current_time: float = 0.0

    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        return self.current_time - self.start_time

    @property
    def progress_percentage(self) -> float:
        """Get progress as percentage (0-100)"""
        if self.total_bytes == 0:
            return 0.0
        return (self.bytes_processed / self.total_bytes) * 100

    @property
    def processing_speed(self) -> float:
        """Get processing speed in bytes per second"""
        if self.elapsed_time == 0:
            return 0.0
        return self.bytes_processed / self.elapsed_time

    @property
    def estimated_time_remaining(self) -> float:
        """Get estimated remaining time in seconds"""
        if self.processing_speed == 0:
            return float('inf')
        remaining_bytes = self.total_bytes - self.bytes_processed
        return remaining_bytes / self.processing_speed


class ProgressTracker:
    """Tracks progress of file operations"""

    def __init__(self, total_bytes: int, callback: Optional[Callable] = None):
        """
        Initialize progress tracker

        Args:
            total_bytes: Total bytes to process
            callback: Optional callback function to call with progress updates
        """
        if total_bytes <= 0:
            raise ValueError("Total bytes must be positive")

        self._stats = ProgressStats(
            total_bytes=total_bytes,
            start_time=time.time(),
            current_time=time.time()
        )
        self._callback = callback

    @property
    def stats(self) -> ProgressStats:
        """Get current progress statistics"""
        return self._stats

    def update(self, bytes_processed: int) -> None:
        """
        Update progress with number of bytes processed

        Args:
            bytes_processed: Number of bytes processed so far
        """
        if bytes_processed < 0:
            raise ValueError("Bytes processed cannot be negative")
        if bytes_processed > self._stats.total_bytes:
            raise ValueError("Bytes processed cannot exceed total bytes")

        self._stats.bytes_processed = bytes_processed
        self._stats.current_time = time.time()

        if self._callback:
            self._callback(self._stats)

    def format_progress(self) -> str:
        """Format current progress as string"""
        stats = self.stats
        return (
            f"Progress: {stats.progress_percentage:.1f}% "
            f"({stats.bytes_processed}/{stats.total_bytes} bytes) | "
            f"Speed: {stats.processing_speed:.1f} bytes/sec | "
            f"Remaining: {stats.estimated_time_remaining:.1f} sec"
        )

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass  # No cleanup needed
