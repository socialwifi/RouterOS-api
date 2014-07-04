def get_bytes(string):
    if hasattr(string, 'encode'):
        return string.encode()
    else:
        return string
