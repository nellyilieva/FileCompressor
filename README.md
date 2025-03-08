# FileCompressor

FileCompressor is a command-line tool designed to compress and decompress files using various algorithms. The tool supports Run-Length Encoding (RLE) and Lempel-Ziv-Welch (LZW) compression algorithms, and provides a user-friendly interface for managing file compression and decompression tasks.

## Features

- **Compression and Decompression**: Compress and decompress files using RLE or LZW algorithms.
- **File Information**: Display detailed information about a file, including size, extension, and last modified date.
- **Progress Tracking**: Real-time progress tracking during compression and decompression operations.
- **Statistics**: View detailed statistics after each operation, including compression ratio, processing speed, and more.

## Available Commands

- **`cf <input_file> <output_file>`**: Compress a file.
- **`dcf <input_file> <output_file>`**: Decompress a file.
- **`rle`**: Select Run-Length Encoding (RLE) algorithm.
- **`lzw`**: Select Lempel-Ziv-Welch (LZW) algorithm.
- **`stat <file_path>`**: Display file information.
- **`exit`**: Exit the program.
- **`help`**: Display the list of available commands.