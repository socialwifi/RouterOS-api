class RouterOsBinaryResource(object):
    def __init__(self, communicator, path):
        self.communicator = communicator
        self.path = clean_path(path)

    def get(self, **kwargs):
        return self.call('print', {}, kwargs)

    def get_async(self, **kwargs):
        return self.call_async('print', {}, kwargs)

    def detailed_get(self, **kwargs):
        return self.call('print', {'detail': ''}, kwargs)

    def detailed_get_async(self, **kwargs):
        return self.call_async('print', {'detail': ''}, kwargs)

    def set(self, **kwargs):
        return self.call('set', kwargs)

    def set_async(self, **kwargs):
        return self.call('set', kwargs)

    def add(self, **kwargs):
        return self.call('add', kwargs)

    def add_async(self, **kwargs):
        return self.call_async('add', kwargs)

    def remove(self, **kwargs):
        return self.call('remove', kwargs)

    def remove_async(self, **kwargs):
        return self.call_async('remove', kwargs)

    def call(self, command, arguments=None, queries=None,
             additional_queries=()):
        return self.call_async(
            command, arguments=arguments, queries=queries, additional_queries=additional_queries,
        ).get()

    def call_async(self, command, arguments=None, queries=None, additional_queries=()):
        return self.communicator.call(
            self.path, command, arguments=arguments, queries=queries,
            additional_queries=additional_queries)

    def __repr__(self):
        return type(self).__name__ + '({path})'.format(path=self.path)


class RouterOsResource(RouterOsBinaryResource):
    def __init__(self, communicator, path, structure):
        self.structure = structure
        super(RouterOsResource, self).__init__(communicator, path)

    def call_async(self, command, arguments=None, queries=None, additional_queries=()):
        arguments = self.transform_dictionary(arguments or {})
        queries = self.transform_dictionary(queries or {})
        promise = self.communicator.call(
            self.path, command, arguments=arguments, queries=queries,
            additional_queries=additional_queries)
        return self.decorate_promise(promise)

    def transform_dictionary(self, dictionary):
        return dict(self.transform_item(item) for item in dictionary.items())

    def transform_item(self, item):
        key, value = item
        if value is None:
            return (key, None)
        else:
            return (key, self.structure[key].get_mikrotik_value(value))

    def decorate_promise(self, promise):
        return TypedPromiseDecorator(promise, self.structure)


class TypedPromiseDecorator(object):
    def __init__(self, inner, structure):
        self.inner = inner
        self.structure = structure

    def __iter__(self):
        return map(self.transform_dictionary, self.inner)

    def get(self):
        response = self.inner.get()
        return response.map(self.transform_dictionary)

    def transform_dictionary(self, row):
        return dict(self.transform_item(item) for item in row.items())

    def transform_item(self, item):
        key, value = item
        if value is None:
            return (key, None)
        else:
            return (key, self.structure[key].get_python_value(value))


def clean_path(path):
    if not path.endswith('/'):
        path += '/'
    if not path.startswith('/'):
        path = '/' + path
    return path
