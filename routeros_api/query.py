class BasicQuery(object):
    operator = None

    def __init__(self, key, value):
        if type(key) is str:
            key = key.encode()
        if type(value) is str:
            value = value.encode()
        self.key = key
        self.value = value

    def get_api_format(self):
        return [self.operator + self.key + b'=' + self.value]


class IsEqualQuery(BasicQuery):
    operator = b'?'


class IsLessQuery(BasicQuery):
    operator = b'?<'


class IsGreaterQuery(BasicQuery):
    operator = b'?>'


class HasValueQuery(object):
    def __init__(self, key):
        if type(key) is str:
            key = key.encode()
        self.key = key

    def get_api_format(self):
        return [b"?" + self.key]


class OperatorQuery(object):
    operator = None

    def __init__(self, *others):
        self.others = others

    def get_api_format(self):
        formated = []
        for other in self.others:
            formated.extend(other.get_api_format())
        operators_count = (len(self.others) - 1)
        formated.append(b'?#' + self.operator * operators_count)


class OrQuery(OperatorQuery):
    operator = b'|'


class AndQuery(OperatorQuery):
    operator = b'&'


class NotQuery(OperatorQuery):
    operator = b'!'
