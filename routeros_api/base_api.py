import socket

LENGTH_MATRIX = [
    (0x80, 0x0),
    (0x40, 0x80),
    (0x20, 0xC0),
    (0x10, 0xE0),
    (0x1, 0xF0),
]

OVER_MAX_LENGTH_MASK = 0xF8

class RouterOsApiError(Exception):
    pass


class Connection(object):
    def __init__(self, socket):
        self.socket = socket

    def send_sentence(self, words):
        for word in words + [b'']:
            full_word = encode_length(len(word)) + word
            self.socket.sendall(full_word)

    def receive_sentence(self):
        try:
            return list(iter(self.receive_word, b''))
        except socket.error as e:
            RouterOsApiError(str(e))

    def receive_word(self):
        result = b''
        length = decode_length(self.socket.recv)
        while len(result) != length:
            received = self.socket.recv(length - len(result))
            assert received
            result += received
        return result


def encode_length(length):
    data, number_of_bytes = _encode_length(length)
    return to_bytes(data, number_of_bytes)


def _encode_length(length):
    if length < 0:
        raise ValueError("Negative length.")

    for bytes, (max_value, mask) in enumerate(LENGTH_MATRIX):
        offset = 8 * bytes
        if length < (max_value << offset):
            return length | (mask << offset), bytes + 1
    raise ValueError("String to long.")


def to_bytes(number, length):
    if hasattr(number, 'to_bytes'):
        return number.to_bytes(length, 'big')
    else:
        result = []
        for byte in reversed(range(length)):
            result.append(chr((number >> (8 * byte)) & 0xff))
        return ''.join(result)


def decode_length(read):
    first = ord(read(1))
    masks = tuple(zip(*LENGTH_MATRIX))[1]
    mask_with_next = zip(masks, masks[1:] + (OVER_MAX_LENGTH_MASK,))
    for bytes, (mask, next_mask) in enumerate(mask_with_next):
        if next_mask & first == mask:
            result = first & ~next_mask
            break
    else:
        raise ValueError
    for _ in range(bytes):
        result <<= 8
        result += ord(read(1))
    return result
