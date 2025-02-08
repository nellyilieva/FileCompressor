from typing import List, Optional
import struct


class BitHandler:
    """Handles bit-level operations for compression algorithms"""

    def __init__(self, buffer_size: int = 8):
        if buffer_size <= 0:
            raise ValueError("Buffer size must be positive")

        self._buffer_size = buffer_size
        self._bit_buffer: List[bool] = []
        self._byte_buffer: bytearray = bytearray()

    @property
    def buffer_size(self) -> int:
        """Get the buffer size in bytes"""
        return self._buffer_size

    @property
    def bits_in_buffer(self) -> int:
        """Get number of bits currently in the buffer"""
        return len(self._bit_buffer)

    def write_bit(self, bit: bool) -> Optional[bytes]:
        """Write a single bit to the buffer"""
        self._bit_buffer.append(bit)

        if len(self._bit_buffer) == 8:
            return self.flush_bits()
        return None

    def write_bits(self, bits: List[bool]) -> bytes:
        """Write multiple bits to the buffer"""
        result = bytearray()

        for bit in bits:
            byte = self.write_bit(bit)
            if byte:
                result.extend(byte)

        return bytes(result)

    def write_byte(self, byte: int) -> bytes:
        """Write a byte as bits"""
        if not 0 <= byte <= 255:
            raise ValueError("Byte value must be between 0 and 255")

        bits = [bool(byte & (1 << i)) for i in range(7, -1, -1)]
        return self.write_bits(bits)

    def write_bytes(self, data: bytes) -> bytes:
        """Write multiple bytes as bits"""
        result = bytearray()

        for byte in data:
            result.extend(self.write_byte(byte))

        return bytes(result)

    def flush_bits(self) -> Optional[bytes]:
        """Flush bits in buffer to a byte, padding with zeros if needed"""
        if not self._bit_buffer:
            return None

        # Pad with zeros if needed
        while len(self._bit_buffer) < 8:
            self._bit_buffer.append(False)

        # Convert bits to byte
        byte = 0
        for i, bit in enumerate(self._bit_buffer):
            if bit:
                byte |= (1 << (7 - i))

        self._bit_buffer.clear()
        return bytes([byte])

    def read_bit(self, data: bytes, bit_position: int) -> tuple[bool, int]:
        """Read a single bit from the given position in data"""
        byte_pos = bit_position // 8
        bit_offset = bit_position % 8

        if byte_pos >= len(data):
            raise IndexError("Bit position out of range")

        byte = data[byte_pos]
        bit = bool(byte & (1 << (7 - bit_offset)))

        return bit, bit_position + 1

    def read_bits(self, data: bytes, bit_position: int, num_bits: int) -> tuple[List[bool], int]:
        """Read multiple bits from the given position"""
        bits = []
        current_position = bit_position

        for i in range(num_bits):
            bit, current_position = self.read_bit(data, current_position)
            bits.append(bit)

        return bits, current_position

    def read_byte(self, data: bytes, bit_position: int) -> tuple[int, int]:
        """Read a byte from the given bit position"""
        bits, new_position = self.read_bits(data, bit_position, 8)

        byte = 0
        for i, bit in enumerate(bits):
            if bit:
                byte |= (1 << (7 - i))

        return byte, new_position
