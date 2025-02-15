from typing import List, Optional
# еми май си има библиотека за това...


class BitHandler:
    def __init__(self, buffer_size=8):
        if buffer_size <= 0:
            raise ValueError("Buffer size must be positive")

        self._buffer_size = buffer_size
        self._bit_buffer: List[bool] = []
        self._byte_buffer: bytearray = bytearray()

    @property
    def buffer_size(self):
        return self._buffer_size

    @property
    def bits_in_buffer(self):
        return len(self._bit_buffer)

    def write_bit(self, bit) -> Optional[bytes]:
        self._bit_buffer.append(bit)

        if len(self._bit_buffer) == 8:
            return self.flush_bits()
        return None

    def write_bits(self, bits) -> bytes:
        result = bytearray()

        for bit in bits:
            byte = self.write_bit(bit)
            if byte:
                result.extend(byte)

        return bytes(result)

    def write_byte(self, byte) -> bytes:
        if not 0 <= byte <= 255:
            raise ValueError("Byte value must be between 0 and 255")

        bits = [bool(byte & (1 << i)) for i in range(7, -1, -1)]
        return self.write_bits(bits)

    def write_bytes(self, data) -> bytes:
        result = bytearray()

        for byte in data:
            result.extend(self.write_byte(byte))

        return bytes(result)

    def flush_bits(self) -> Optional[bytes]:
        if not self._bit_buffer:
            return None

        while len(self._bit_buffer) < 8:
            self._bit_buffer.append(False)

        byte = 0
        for i, bit in enumerate(self._bit_buffer):
            if bit:
                byte |= (1 << (7 - i))

        self._bit_buffer.clear()
        return bytes([byte])

    def read_bit(self, data: bytes, bit_position) -> tuple[bool, int]:
        byte_pos = bit_position // 8
        bit_offset = bit_position % 8

        if byte_pos >= len(data):
            raise IndexError("Bit position out of range")

        byte = data[byte_pos]
        bit = bool(byte & (1 << (7 - bit_offset)))

        return bit, bit_position + 1

    def read_bits(self, data: bytes, bit_position, num_bits) -> tuple[List[bool], int]:
        bits = []
        current_position = bit_position

        for i in range(num_bits):
            bit, current_position = self.read_bit(data, current_position)
            bits.append(bit)

        return bits, current_position

    def read_byte(self, data: bytes, bit_position) -> tuple[int, int]:
        bits, new_position = self.read_bits(data, bit_position, 8)

        byte = 0
        for i, bit in enumerate(bits):
            if bit:
                byte |= (1 << (7 - i))

        return byte, new_position
