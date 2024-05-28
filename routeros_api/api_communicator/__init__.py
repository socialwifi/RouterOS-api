from routeros_api.api_communicator import async_decorator
from routeros_api.api_communicator import base
from routeros_api.api_communicator import encoding_decorator
from routeros_api.api_communicator import exception_decorator
from routeros_api.api_communicator import key_cleaner_decorator


class ApiCommunicator(encoding_decorator.EncodingApiCommunicator):
    def __init__(self, base_api):
        communicator = base.ApiCommunicatorBase(base_api)

        key_cleaner_communicator = (
            key_cleaner_decorator.KeyCleanerApiCommunicator(communicator))

        self.exception_aware_communicator = (
            exception_decorator.ExceptionAwareApiCommunicator(
                key_cleaner_communicator))

        async_communicator = async_decorator.AsyncApiCommunicator(
            self.exception_aware_communicator)

        super(ApiCommunicator, self).__init__(async_communicator)

    def add_exception_handler(self, exception_handler):
        self.exception_aware_communicator.add_handler(exception_handler)
