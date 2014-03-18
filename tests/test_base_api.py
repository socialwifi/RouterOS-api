from unittest import TestCase


from routeros_api import base_api


class TestEncodeLength(TestCase):
    def test_zero(self):
        result = base_api._encode_length(0)
        expected_number = 0
        expected_length = 1
        expected = (expected_number, expected_length)
        self.assertEqual(expected, result)

    def test_one(self):
        result = base_api._encode_length(1)
        expected_number = 1
        expected_length = 1
        expected = (expected_number, expected_length)
        self.assertEqual(expected, result)

    def test_over_0x80(self):
        result = base_api._encode_length(300)
        expected_number = 33068
        expected_length = 2
        expected = (expected_number, expected_length)
        self.assertEqual(expected, result)

    def test_over_0x3FFF(self):
        result = base_api._encode_length(17000)
        expected_number = 12599912
        expected_length = 3
        expected = (expected_number, expected_length)
        self.assertEqual(expected, result)

    def test_to_big(self):
        self.assertRaises(ValueError, base_api._encode_length, 2 ** 128)


class TestToBytes(TestCase):
    def test_zero(self):
        result = base_api.to_bytes(0, 1)
        expected = b'\x00'
        self.assertEqual(expected, result)

    def test_multiple_bytes(self):
        result = base_api.to_bytes(0x1112, 2)
        expected = b'\x11\x12'
        self.assertEqual(expected, result)
