class EncodingApiCommunicator(object):
    def __init__(self, inner):
        self.inner = inner

    def call(self, path, command, arguments=None, queries=None,
                   additional_queries=(), include_done=False):
        path = path.encode()
        command = command.encode()
        arguments = self.transform_dictionary(arguments or {})
        queries = self.transform_dictionary(queries or {})
        promise = self.inner.call(
            path, command, arguments, queries, additional_queries,
            include_done)
        return self.decorate_promise(promise)

    def transform_dictionary(self, dictionary):
        return dict(self.transform_item(item) for item in dictionary.items())

    def transform_item(self, item):
        key, value = item
        return (key.encode(), value)

    def decorate_promise(self, promise):
        return EncodedPromiseDecorator(promise)



class EncodedPromiseDecorator(object):
    def __init__(self, inner):
        self.inner = inner

    def get(self):
        response = self.inner.get()
        return [self.transform_row(row) for row in response]

    def transform_row(self, row):
        return dict(self.transform_item(item) for item in row.items())

    def transform_item(self, item):
        key, value = item
        return (key.decode(), value)
