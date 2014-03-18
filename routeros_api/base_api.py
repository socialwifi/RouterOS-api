LENGTH_MATRIX = [
    (0x80, 0x0),
    (0x40, 0x80),
    (0x20, 0xC0),
    (0x10, 0xE0),
    (0x1, 0xF0),
]


def encode_length(length):
    data, number_of_bytes = _encode_length(length)
    return to_bytes(data, number_of_bytes)


def _encode_length(length):
    if length < 0:
        raise TypeError("Negative length.")

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
