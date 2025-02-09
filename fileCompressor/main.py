import argparse
from pathlib import Path
import sys
import time
from compressors.rle import RLECompressor


def format_size(size_in_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f} TB"


def format_time(seconds: float) -> str:
    """Format time duration in human readable format"""
    if seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} seconds"
    else:
        minutes = int(seconds // 60)
        seconds = seconds % 60
        return f"{minutes} minutes {seconds:.2f} seconds"


def process_file(compressor: RLECompressor, input_path: Path, output_path: Path, mode: str):
    """Process a file with the given compressor and mode"""
    try:
        start_time = time.time()

        # Perform compression or decompression
        if mode == 'compress':
            print(f"Compressing {input_path}...")
            compressor.compress(input_path, output_path)
        else:
            print(f"Decompressing {input_path}...")
            compressor.decompress(input_path, output_path)

        # Get and display statistics
        stats = compressor.get_compression_stats()
        end_time = time.time()

        print("\nOperation completed successfully!")
        print(f"Input size: {format_size(stats['original_size'])}")
        print(f"Output size: {format_size(stats['compressed_size'])}")

        if mode == 'compress':
            ratio = (1 - stats['compressed_size'] / stats['original_size']) * 100
            print(f"Compression ratio: {ratio:.1f}% reduction")

        print(f"Time taken: {format_time(end_time - start_time)}")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def main():
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description="RLE file compression utility")
    parser.add_argument('mode', choices=['compress', 'decompress'],
                        help='Operation mode: compress or decompress')
    parser.add_argument('input', type=Path,
                        help='Path to input file')
    parser.add_argument('output', type=Path,
                        help='Path to output file')
    parser.add_argument('--test', action='store_true',
                        help='Create and compress a test file')

    args = parser.parse_args()

    # Create test file if requested
    if args.test:
        print("Creating test file...")
        with open(args.input, 'wb') as f:
            # Write some test patterns
            f.write(b'A' * 1000)  # 1000 'A's
            f.write(b'B' * 500)  # 500 'B's
            f.write(b'C' * 200)  # 200 'C's
            f.write(bytes(range(65, 91)))  # A-Z
        print(f"Test file created: {args.input}")

    # Verify input file exists
    if not args.test and not args.input.exists():
        print(f"Error: Input file '{args.input}' does not exist", file=sys.stderr)
        sys.exit(1)

    # Verify output directory exists
    if not args.output.parent.exists():
        print(f"Creating output directory: {args.output.parent}")
        args.output.parent.mkdir(parents=True)

    # Create compressor and process file
    compressor = RLECompressor()
    process_file(compressor, args.input, args.output, args.mode)


if __name__ == '__main__':
    main()
