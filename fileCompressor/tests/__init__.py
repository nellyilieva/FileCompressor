import os
from pathlib import Path


def get_test_files_path() -> Path:
    """Returns path to test files directory"""
    return Path(__file__).parent / 'test_files'


def setup_test_files():
    """Create test files directory if it doesn't exist"""
    test_files_path = get_test_files_path()
    if not test_files_path.exists():
        os.makedirs(test_files_path)
