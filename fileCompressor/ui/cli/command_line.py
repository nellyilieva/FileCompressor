from pathlib import Path
import time
from compressors.rle import RLECompressor


def format_size(size_in_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f} TB"


def get_file_info(file_path: Path) -> str:
    """Get formatted file information"""
    try:
        stats = file_path.stat()
        return (f"\nFile Information:"
                f"\nPath: {file_path}"
                f"\nSize: {format_size(stats.st_size)}"
                f"\nLast modified: {time.ctime(stats.st_mtime)}")
    except Exception as e:
        return f"\nError getting file info: {str(e)}"


def process_file(compressor: RLECompressor, input_path: Path, output_path: Path, mode: str) -> bool:
    """Process a file with the given compressor and mode"""
    try:
        start_time = time.time()

        if mode == 'compress':
            print(f"\nCompressing {input_path}...")
            compressor.compress(input_path, output_path)
        else:
            print(f"\nDecompressing {input_path}...")
            compressor.decompress(input_path, output_path)

        stats = compressor.get_compression_stats()
        end_time = time.time()

        print("\nOperation completed successfully!")
        print(f"Input size: {format_size(stats['original_size'])}")
        print(f"Output size: {format_size(stats['compressed_size'])}")

        if mode == 'compress':
            ratio = (1 - stats['compressed_size'] / stats['original_size']) * 100
            print(f"Compression ratio: {ratio:.1f}% reduction")

        print(f"Time taken: {(end_time - start_time):.2f} seconds")
        return True

    except Exception as e:
        print(f"\nError: {str(e)}")
        return False


def main():
    compressor = RLECompressor()

    while True:
        print("\n=== RLE File Compression Utility ===")
        print("1. Compress a file")
        print("2. Decompress a file")
        print("3. View file information")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == '4':
            break

        if choice not in ['1', '2', '3']:
            print("\nInvalid choice. Please try again.")
            continue

        # Get input file path
        input_file = input("\nEnter input file path: ").strip()
        input_path = Path(input_file)

        if not input_path.exists():
            print(f"\nError: File '{input_file}' does not exist")
            continue

        if choice == '3':
            # Display file information
            print(get_file_info(input_path))
            continue

        # Get output file path
        output_file = input("Enter output file path: ").strip()
        output_path = Path(output_file)

        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Process the file
        if choice == '1':
            process_file(compressor, input_path, output_path, 'compress')
        else:  # choice == '2'
            process_file(compressor, input_path, output_path, 'decompress')


if __name__ == '__main__':
    main()
