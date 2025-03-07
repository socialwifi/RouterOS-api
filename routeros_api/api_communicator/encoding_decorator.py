import logging

logger = logging.getLogger(__name__)


class EncodingApiCommunicator(object):
    def __init__(self, inner):
        self.inner = inner

    def call(self, path, command, arguments=None, queries=None, additional_queries=()):
        path = path.encode()
        command = command.encode()
        arguments = self.transform_dictionary(arguments or {})
        queries = self.transform_dictionary(queries or {})
        promise = self.inner.call(
            path, command, arguments, queries, additional_queries)
        return self.decorate_promise(promise)

    def transform_dictionary(self, dictionary):
        return dict(self.transform_item(item) for item in dictionary.items())

    def transform_item(self, item):
        key, value = item
        if value is not None and not isinstance(value, bytes):
            logger.warning(
                'Non-bytes value passed as item value ({}). You should probably use api.get_resource() instead of '
                'api.get_binary_resource() or encode arguments yourself.'.format(value))
            value = value.encode()
        return (key.encode(), value)

    def decorate_promise(self, promise):
        return EncodedPromiseDecorator(promise)


class EncodedPromiseDecorator(object):
    def __init__(self, inner):
        self.inner = inner

    def get(self):
        response = self.inner.get()
        return response.map(self.transform_row)

    def __iter__(self):
        return map(self.transform_row, self.inner)

    def transform_row(self, row):
        return dict(self.transform_item(item) for item in row.items())

    def transform_item(self, item):
        key, value = item
        return (key.decode(), value)
