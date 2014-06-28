from routeros_api.api_communicator import base
from routeros_api.api_communicator import exception_decorator
from routeros_api.api_communicator import encoding_decorator

def ApiCommunicator(base_api, exception_handler):
    communicator = base.ApiCommunicatorBase(base_api)
    exception_aware_communicator = (
        exception_decorator.ExceptionAwareApiCommunicator(communicator))
    exception_aware_communicator.add_handler(exception_handler)
    encoding_communicator = encoding_decorator.EncodingApiCommunicator(
        exception_aware_communicator)
    return encoding_communicator
