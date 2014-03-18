def encode_length(length):
    data, number_of_bytes = _encode_length(length)
    return to_bytes(data, number_of_bytes)


def _encode_length(length):
    x = [
        (0x7F, 0x0),
        (0x3FFF, 0x80),
        (0x1FFFFF, 0xC0),
        (0xFFFFFFF, 0xE0),
        (0xFFFFFFFF, 0xF0),
    ]
    if length < 0:
        raise TypeError("Negative length.")
    for bytes, (max_value, mask) in enumerate(x):
        if length <= max_value:
            return length | (mask << 8 * bytes), bytes + 1
    raise ValueError("String to long.")


def to_bytes(number, length):
    if hasattr(number, 'to_bytes'):
        return number.to_bytes(length, 'big')
    else:
        result = []
        for byte in reversed(range(length)):
            result.append(chr((number >> (8 * byte)) & 0xff))
        return ''.join(result)
