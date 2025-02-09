import unittest
import time
from utils.progress_tracker import ProgressTracker, ProgressStats


class TestProgressTracker(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.total_bytes = 1000
        self.tracker = ProgressTracker(self.total_bytes)

    def test_initialization(self):
        """Test progress tracker initialization"""
        stats = self.tracker.stats

        self.assertEqual(stats.total_bytes, self.total_bytes)
        self.assertEqual(stats.bytes_processed, 0)
        self.assertGreater(stats.start_time, 0)
        self.assertEqual(stats.progress_percentage, 0.0)

        with self.assertRaises(ValueError):
            ProgressTracker(0)
        with self.assertRaises(ValueError):
            ProgressTracker(-100)

    def test_update_progress(self):
        """Test updating progress"""
        self.tracker.update(500)  # 50% progress
        stats = self.tracker.stats

        self.assertEqual(stats.bytes_processed, 500)
        self.assertEqual(stats.progress_percentage, 50.0)

        with self.assertRaises(ValueError):
            self.tracker.update(-1)
        with self.assertRaises(ValueError):
            self.tracker.update(self.total_bytes + 1)

    def test_callback(self):
        """Test progress callback"""
        callback_called = False
        callback_stats = None

        def callback(stats):
            nonlocal callback_called, callback_stats
            callback_called = True
            callback_stats = stats

        tracker = ProgressTracker(self.total_bytes, callback)
        tracker.update(500)

        self.assertTrue(callback_called)
        self.assertIsNotNone(callback_stats)
        self.assertEqual(callback_stats.bytes_processed, 500)

    def test_progress_stats(self):
        """Test progress statistics calculations"""
        # Simulate processing with delays
        start_time = time.time()
        stats = ProgressStats(
            bytes_processed=500,
            total_bytes=1000,
            start_time=start_time,
            current_time=start_time + 2.0  # 2 seconds elapsed
        )

        self.assertEqual(stats.progress_percentage, 50.0)
        self.assertEqual(stats.elapsed_time, 2.0)
        self.assertEqual(stats.processing_speed, 250.0)  # 500 bytes / 2 seconds
        self.assertEqual(stats.estimated_time_remaining, 2.0)  # Same speed for remaining

    def test_zero_time_edge_cases(self):
        """Test edge cases with zero elapsed time"""
        stats = ProgressStats(
            bytes_processed=0,
            total_bytes=1000,
            start_time=time.time(),
            current_time=time.time()
        )

        self.assertEqual(stats.progress_percentage, 0.0)
        self.assertEqual(stats.elapsed_time, 0.0)
        self.assertEqual(stats.processing_speed, 0.0)
        self.assertEqual(stats.estimated_time_remaining, float('inf'))

    def test_format_progress(self):
        """Test progress string formatting"""
        self.tracker.update(500)
        progress_str = self.tracker.format_progress()

        self.assertIn("50.0%", progress_str)
        self.assertIn("500/1000 bytes", progress_str)
        self.assertIn("bytes/sec", progress_str)
        self.assertIn("sec", progress_str)

    def test_context_manager(self):
        """Test context manager functionality"""
        with ProgressTracker(1000) as tracker:
            tracker.update(500)
            self.assertEqual(tracker.stats.progress_percentage, 50.0)


if __name__ == '__main__':
    unittest.main()
