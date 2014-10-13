import re
from routeros_api import exceptions


class ExceptionHandler(object):
    def __init__(self, message_to_class_map):
        self.message_to_class_map = message_to_class_map

    def handle(self, exception):
        if isinstance(exception, exceptions.RouterOsApiCommunicationError):
            self._handle_communication_exception(exception)

    def _handle_communication_exception(self, exception):
        for message, exception_class in self.message_to_class_map:
            if re.match(message, exception.original_message):
                raise exception_class(exception, exception.original_message)
