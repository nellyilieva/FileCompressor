# from pathlib import Path
# import heapq
# import time
# from collections import Counter
# from typing import Dict, Optional
# from core.interfaces.compressor import BaseCompressor
# from utils.bit_handler import BitHandler
# from utils.progress_tracker import ProgressTracker
# from utils.file_handler import FileHandler
#
#
# class HuffmanNode:
#     def __init__(self, char: Optional[int], freq: int):
#         self.char = char  # Byte value (0-255) or None for internal nodes
#         self.freq = freq  # Frequency of the byte
#         self.left = None  # Left child
#         self.right = None  # Right child
#
#     def __lt__(self, other):
#         return self.freq < other.freq
#
#
# class HuffmanCompressor(BaseCompressor):
#     def __init__(self):
#         self.codes: Dict[int, str] = {}  # Maps bytes to their Huffman codes
#         self.reverse_codes: Dict[str, int] = {}  # Maps Huffman codes to bytes
#         self.stats: Dict[str, float] = {}  # Compression statistics
#
#     def _build_tree(self, text: bytes) -> Optional[HuffmanNode]:
#         """Build the Huffman tree from the frequency of bytes."""
#         if not text:
#             return None
#
#         freq = Counter(text)
#         heap = [HuffmanNode(char, frequency) for char, frequency in freq.items()]
#         heapq.heapify(heap)
#
#         while len(heap) > 1:
#             left = heapq.heappop(heap)
#             right = heapq.heappop(heap)
#             merged = HuffmanNode(None, left.freq + right.freq)
#             merged.left, merged.right = left, right
#             heapq.heappush(heap, merged)
#
#         return heap[0] if heap else None
#
#     def _build_codes(self, node: Optional[HuffmanNode], code: str = ''):
#         """Build Huffman codes by traversing the tree."""
#         if node is None:
#             return
#
#         if node.char is not None:  # Leaf node
#             self.codes[node.char] = code
#             self.reverse_codes[code] = node.char
#         else:
#             self._build_codes(node.left, code + "0")
#             self._build_codes(node.right, code + "1")
#
#     def _serialize_tree(self, node: Optional[HuffmanNode]) -> bytes:
#         """Serialize the Huffman tree into bytes."""
#         if node is None:
#             return b'\x00'
#
#         if node.char is not None:
#             return b'\x01' + bytes([node.char])
#
#         return b'\x00' + self._serialize_tree(node.left) + self._serialize_tree(node.right)
#
#     def _deserialize_tree(self, data: bytes, index: int = 0) -> tuple[Optional[HuffmanNode], int]:
#         """Deserialize the Huffman tree from bytes."""
#         if index >= len(data):
#             return None, index
#
#         if data[index] == 1:  # Leaf node
#             return HuffmanNode(data[index + 1], 0), index + 2
#         elif data[index] == 0:  # Internal node
#             left, next_index = self._deserialize_tree(data, index + 1)
#             right, final_index = self._deserialize_tree(data, next_index)
#             node = HuffmanNode(None, 0)
#             node.left, node.right = left, right
#             return node, final_index
#
#         return None, index
#
#     def compress(self, input_file: Path, output_file: Path):
#         """Compress a file using Huffman coding."""
#         start_time = time.time()
#
#         # Read input file
#         with FileHandler() as fh:
#             fh.open_file(input_file, 'rb')
#             text = fh.read_chunk(fh.file_size)
#
#         if not text:
#             with FileHandler() as fh:
#                 fh.open_file(output_file, 'wb')
#                 fh.write_chunk(b'')
#             self.stats = {
#                 'original_size': 0,
#                 'compressed_size': 0,
#                 'compression_ratio': 1.0,
#                 'time_taken': time.time() - start_time
#             }
#             return
#
#         # Build Huffman tree and codes
#         root = self._build_tree(text)
#         self._build_codes(root)
#
#         # Convert text to compressed bits
#         bit_handler = BitHandler()
#         for byte in text:
#             bit_handler.write_bits([bit == '1' for bit in self.codes[byte]])
#
#         # Add padding
#         padding = (8 - bit_handler.bits_in_buffer % 8) % 8
#         for _ in range(padding):
#             bit_handler.write_bit(False)
#
#         # Flush remaining bits
#         compressed_bytes = bit_handler.flush_bits() or b''  # Ensure compressed_bytes is not None
#
#         # Write compressed data
#         with FileHandler() as fh:
#             fh.open_file(output_file, 'wb')
#             tree_data = self._serialize_tree(root)
#             fh.write_chunk(len(tree_data).to_bytes(4, 'big'))
#             fh.write_chunk(tree_data)
#             fh.write_chunk(padding.to_bytes(1, 'big'))
#             fh.write_chunk(compressed_bytes)
#
#         compressed_size = output_file.stat().st_size
#         original_size = len(text)
#         self.stats = {
#             'original_size': original_size,
#             'compressed_size': compressed_size,
#             'compression_ratio': compressed_size / original_size if original_size > 0 else 1.0,
#             'time_taken': time.time() - start_time
#         }
#
#     def decompress(self, input_file: Path, output_file: Path):
#         """Decompress a file using Huffman coding."""
#         start_time = time.time()
#
#         with FileHandler() as fh:
#             fh.open_file(input_file, 'rb')
#
#             # Handle empty file
#             if input_file.stat().st_size == 0:
#                 with FileHandler() as fh_out:
#                     fh_out.open_file(output_file, 'wb')
#                     fh_out.write_chunk(b'')
#                 self.stats = {
#                     'original_size': 0,
#                     'decompressed_size': 0,
#                     'time_taken': time.time() - start_time
#                 }
#                 return
#
#             # Read the tree size and tree data
#             tree_size = int.from_bytes(fh.read_chunk(4), 'big')
#             tree_data = fh.read_chunk(tree_size)
#
#             # Read padding and compressed data
#             padding = int.from_bytes(fh.read_chunk(1), 'big')
#             compressed_data = fh.read_chunk(fh.file_size - fh._current_file.tell())
#
#         # Deserialize the tree
#         root, _ = self._deserialize_tree(tree_data)
#         if root is None:
#             raise ValueError("Invalid Huffman tree data")
#
#         # Rebuild codes from the tree
#         self.codes.clear()
#         self.reverse_codes.clear()
#         self._build_codes(root)
#
#         # Convert bytes to bits and remove padding
#         bit_handler = BitHandler()
#         for byte in compressed_data:
#             bit_handler.write_byte(byte)
#         bits = ''.join(str(int(bit)) for bit in bit_handler._bit_buffer)
#         bits = bits[:-padding] if padding else bits
#
#         # Decode using the tree
#         current_code = ''
#         decoded = bytearray()
#         for bit in bits:
#             current_code += bit
#             if current_code in self.reverse_codes:
#                 decoded.append(self.reverse_codes[current_code])
#                 current_code = ''
#
#         # Write decompressed data
#         with FileHandler() as fh:
#             fh.open_file(output_file, 'wb')
#             fh.write_chunk(decoded)
#
#         original_size = input_file.stat().st_size
#         decompressed_size = len(decoded)
#         self.stats = {
#             'original_size': original_size,
#             'decompressed_size': decompressed_size,
#             'time_taken': time.time() - start_time
#         }
#
#     def get_compression_stats(self):
#         """Return a copy of compression statistics."""
#         return self.stats.copy()