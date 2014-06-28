from routeros_api import api_communicator
from routeros_api import exceptions


class ExceptionAwareApiCommunicator(api_communicator.ApiCommunicator):
    def __init__(self, base):
        super(ExceptionAwareApiCommunicator, self).__init__(base)
        self.exception_handler = ExceptionMultiHandler()

    def send_command(self, command):
        try:
            super(ExceptionAwareApiCommunicator, self).send_command(command)
        except exceptions.RouterOsApiError as e:
            self.exception_handler.handle(e)
            raise

    def receive(self, tag):
        try:
            return super(ExceptionAwareApiCommunicator, self).receive(tag)
        except exceptions.RouterOsApiError as e:
            self.exception_handler.handle(e)
            raise

    def add_handler(self, handler):
        self.exception_handler.add_handler(handler)


class ExceptionMultiHandler(object):
    def __init__(self):
        self.subhandlers = []

    def add_handler(self, handler):
        self.subhandlers.append(handler)

    def handle(self, exception):
        for subhandler in self.subhandlers:
            subhandler.handle(exception)
