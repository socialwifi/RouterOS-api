import socket

from routeros_api import exceptions

LENGTH_MATRIX = [
    (0x80, 0x0),
    (0x40, 0x80),
    (0x20, 0xC0),
    (0x10, 0xE0),
    (0x1, 0xF0),
]

OVER_MAX_LENGTH_MASK = 0xF8


class Connection(object):
    def __init__(self, socket):
        self.socket = socket

    def send_sentence(self, words):
        try:
            for word in words + [b'']:
                full_word = encode_length(len(word)) + word
                self.socket.send(full_word)
        except socket.error as e:
            raise exceptions.RouterOsApiConnectionError(str(e))

    def receive_sentence(self):
        try:
            return list(iter(self.receive_word, b''))
        except socket.error as e:
            raise exceptions.RouterOsApiConnectionError(str(e))

    def receive_word(self):
        result = []
        result_length = 0
        expected_length = decode_length(self.socket.receive)
        while result_length != expected_length:
            received = self.socket.receive(expected_length - result_length)
            result.append(received)
            result_length += len(received)
            assert result_length <= expected_length
        return b''.join(result)


def encode_length(length):
    data, number_of_bytes = _encode_length(length)
    return to_bytes(data, number_of_bytes)


def _encode_length(length):
    if length < 0:
        raise exceptions.FatalRouterOsApiError("Negative length.")

    for bytes, (max_value, mask) in enumerate(LENGTH_MATRIX):
        offset = 8 * bytes
        if length < (max_value << offset):
            return length | (mask << offset), bytes + 1
    raise exceptions.FatalRouterOsApiError("String to long.")


def to_bytes(number, length):
    if hasattr(number, 'to_bytes'):
        return number.to_bytes(length, 'big')
    else:
        result = []
        for byte in reversed(range(length)):
            result.append(chr((number >> (8 * byte)) & 0xff))
        return b''.join(result)


def decode_length(read):
    first = ord(read(1))
    masks = tuple(zip(*LENGTH_MATRIX))[1]
    mask_with_next = zip(masks, masks[1:] + (OVER_MAX_LENGTH_MASK,))
    for bytes, (mask, next_mask) in enumerate(mask_with_next):
        if next_mask & first == mask:
            result = first & ~next_mask
            break
    else:
        raise exceptions.FatalRouterOsApiError("Malformed length")
    for _ in range(bytes):
        result <<= 8
        result += ord(read(1))
    return result
