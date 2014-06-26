from routeros_api import api_communicator
from routeros_api import exceptions


class ExceptionAwareApiCommunicator(api_communicator.ApiCommunicator):
    def __init__(self, base):
        super(ExceptionAwareApiCommunicator, self).__init__(base)
        self.exception_handler = ExceptionMultiHandler()

    def call(self, *args, **kwargs):
        try:
            return super(ExceptionAwareApiCommunicator, self).call(
                *args, **kwargs)
        except exceptions.RouterOsApiError as e:
            self.exception_handler.handle(e)
            raise

    def call_async(self, *args, **kwargs):
        try:
            promise = super(ExceptionAwareApiCommunicator, self).call_async(
                *args, **kwargs)
            return ExceptionAwareResponsePromiseDecorator(
                promise, self.exception_handler)
        except exceptions.RouterOsApiError as e:
            self.exception_handler.handle(e)
            raise

    def add_handler(self, handler):
        self.exception_handler.add_handler(handler)


class ExceptionAwareResponsePromiseDecorator(object):
    def __init__(self, decorated, exception_handler):
        self.decorated = decorated
        self.exception_handler = exception_handler

    def get(self):
        try:
            return self.decorated.get()
        except exceptions.RouterOsApiError as e:
            self.exception_handler.handle(e)
            raise


class ExceptionMultiHandler(object):
    def __init__(self):
        self.subhandlers = []

    def add_handler(self, handler):
        self.subhandlers.append(handler)

    def handle(self, exception):
        for subhandler in self.subhandlers:
            subhandler.handle(exception)
