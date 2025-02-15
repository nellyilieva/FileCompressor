import unittest
from utils.bit_handler import BitHandler


class TestBitHandler(unittest.TestCase):
    def setUp(self):
        self.handler = BitHandler()

    def test_initialization(self):
        self.assertEqual(self.handler.buffer_size, 8)
        self.assertEqual(self.handler.bits_in_buffer, 0)

        with self.assertRaises(ValueError):
            BitHandler(buffer_size=0)

        with self.assertRaises(ValueError):
            BitHandler(buffer_size=-1)

    def test_write_bit(self):
        for i in range(7):
            result = self.handler.write_bit(True)
            self.assertIsNone(result)
            self.assertEqual(self.handler.bits_in_buffer, i + 1)

        result = self.handler.write_bit(True)
        self.assertEqual(result, bytes([255]))
        self.assertEqual(self.handler.bits_in_buffer, 0)

    def test_write_bits(self):
        bits = [True, False, True, False, True, False, True, False]
        result = self.handler.write_bits(bits)
        self.assertEqual(result, bytes([0xAA]))
        self.assertEqual(self.handler.bits_in_buffer, 0)

    def test_write_byte(self):
        result = self.handler.write_byte(0xA5)
        self.assertEqual(result, bytes([0xA5]))
        self.assertEqual(self.handler.bits_in_buffer, 0)

        with self.assertRaises(ValueError):
            self.handler.write_byte(256)
        with self.assertRaises(ValueError):
            self.handler.write_byte(-1)

    def test_write_bytes(self):
        data = bytes([0xA5, 0x5A])
        result = self.handler.write_bytes(data)
        self.assertEqual(result, data)
        self.assertEqual(self.handler.bits_in_buffer, 0)

    def test_flush_bits(self):
        for i in range(5):
            self.handler.write_bit(True)

        result = self.handler.flush_bits()
        self.assertEqual(result, bytes([0xF8]))
        self.assertEqual(self.handler.bits_in_buffer, 0)

        result = self.handler.flush_bits()
        self.assertIsNone(result)

    def test_read_bit(self):
        data = bytes([0xA5])

        expected_bits = [True, False, True, False, False, True, False, True]
        position = 0

        for expected in expected_bits:
            bit, position = self.handler.read_bit(data, position)
            self.assertEqual(bit, expected)

        with self.assertRaises(IndexError):
            self.handler.read_bit(data, 8)

    def test_read_bits(self):
        data = bytes([0xA5])

        bits, position = self.handler.read_bits(data, 0, 4)
        self.assertEqual(bits, [True, False, True, False])
        self.assertEqual(position, 4)

        bits, position = self.handler.read_bits(data, position, 4)
        self.assertEqual(bits, [False, True, False, True])
        self.assertEqual(position, 8)

    def test_read_byte(self):
        data = bytes([0xA5, 0x5A])

        byte, position = self.handler.read_byte(data, 0)
        self.assertEqual(byte, 0xA5)
        self.assertEqual(position, 8)

        byte, position = self.handler.read_byte(data, position)
        self.assertEqual(byte, 0x5A)
        self.assertEqual(position, 16)

    def test_integration(self):
        original_data = bytes([0xA5, 0x5A, 0xF0])

        written = self.handler.write_bytes(original_data)
        self.assertEqual(written, original_data)

        position = 0
        read_data = bytearray()

        while position < len(written) * 8:
            byte, position = self.handler.read_byte(written, position)
            read_data.append(byte)

        self.assertEqual(bytes(read_data), original_data)


if __name__ == '__main__':
    unittest.main()
