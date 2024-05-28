import re

from routeros_api import exceptions


class ExceptionHandler(object):
    def __init__(self):
        self.message_to_class_map = []

    def add_exception_type(self, message_re, exception_class):
        self.message_to_class_map.append((message_re, exception_class))

    def handle(self, exception):
        if isinstance(exception, exceptions.RouterOsApiCommunicationError):
            self._handle_communication_exception(exception)

    def _handle_communication_exception(self, exception):
        for message_re, exception_class in self.message_to_class_map:
            if re.search(message_re, exception.original_message):
                raise exception_class(exception, exception.original_message)
