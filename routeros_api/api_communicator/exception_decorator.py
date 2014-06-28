from routeros_api import exceptions


class ExceptionAwareApiCommunicator(object):
    def __init__(self, inner):
        self.inner = inner
        self.exception_handlers = []

    def send(self, *args, **kwargs):
        try:
            return self.inner.send(*args, **kwargs)
        except exceptions.RouterOsApiError as e:
            self.handle_exception(e)
            raise

    def receive(self, tag):
        try:
            return self.inner.receive(tag)
        except exceptions.RouterOsApiError as e:
            self.handle_exception(e)
            raise

    def add_handler(self, handler):
        self.exception_handlers.append(handler)

    def handle_exception(self, exception):
        for subhandler in self.exception_handlers:
            subhandler.handle(exception)
