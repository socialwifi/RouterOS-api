from routeros_api import exceptions


class ExceptionAwareApiCommunicator(object):
    def __init__(self, inner):
        self.inner = inner
        self.exception_handlers = []

    def call_async(self, *args, **kwargs):
        try:
            promise = self.inner.call_async(*args, **kwargs)
            return ExceptionAwarePromise(promise, self)
        except exceptions.RouterOsApiError as e:
            self.handle_exception(e)
            raise

    def add_handler(self, handler):
        self.exception_handlers.append(handler)

    def handle_exception(self, exception):
        for subhandler in self.exception_handlers:
            subhandler.handle(exception)


class ExceptionAwarePromise(object):
    def __init__(self, inner, receiver):
        self.inner = inner
        self.receiver = receiver

    def get(self):
        try:
            return self.inner.get()
        except exceptions.RouterOsApiError as e:
            self.receiver.handle_exception(e)
            raise