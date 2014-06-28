from routeros_api import api_communicator
from routeros_api import exceptions


class ExceptionAwareApiCommunicator(api_communicator.ApiCommunicator):
    def __init__(self, base):
        super(ExceptionAwareApiCommunicator, self).__init__(base)
        self.exception_handlers = []

    def send_command(self, command):
        try:
            super(ExceptionAwareApiCommunicator, self).send_command(command)
        except exceptions.RouterOsApiError as e:
            self.handle_exception(e)
            raise

    def receive(self, tag):
        try:
            return super(ExceptionAwareApiCommunicator, self).receive(tag)
        except exceptions.RouterOsApiError as e:
            self.handle_exception(e)
            raise

    def add_handler(self, handler):
        self.exception_handlers.append(handler)

    def handle_exception(self, exception):
        for subhandler in self.exception_handlers:
            subhandler.handle(exception)
