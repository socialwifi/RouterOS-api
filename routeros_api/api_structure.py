import collections


class StringField(object):
    def get_mikrotik_value(self, string):
        return string.encode()

    def get_python_value(self, bytes):
        return bytes.decode()


class BytesField:
    def get_mikrotik_value(self, bytes):
        return bytes

    def get_python_value(self, bytes):
        return bytes


class BooleanField:
    def get_mikrotik_value(self, condition):
        return b'yes' if condition else b'no'

    def get_python_value(self, bytes):
        assert bytes in (b'yes', b'true', b'no', b'false')
        return bytes in (b'yes', b'true')


default_structure = collections.defaultdict(StringField)
