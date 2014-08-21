import collections


class StringField(object):
    def get_mikrotik_value(self, string):
        return string.encode()

    def get_python_value(self, bytes):
        return bytes.decode()

default_structure = collections.defaultdict(StringField)
