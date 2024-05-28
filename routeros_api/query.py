from routeros_api import utils


class BasicQuery(object):
    operator = None

    def __init__(self, key, value):
        self.key = utils.get_bytes(key)
        self.value = utils.get_bytes(value)

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
        self.key = utils.get_bytes(key)

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
        return formated


class OrQuery(OperatorQuery):
    operator = b'|'


class AndQuery(OperatorQuery):
    operator = b'&'


class NandQuery(AndQuery):
    def get_api_format(self):
        formated = super(NandQuery, self).get_api_format()
        formated[-1] += b'!'
        return formated
