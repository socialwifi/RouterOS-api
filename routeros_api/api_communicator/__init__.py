from routeros_api.api_communicator import base
from routeros_api.api_communicator import exception_decorator

def ApiCommunicator(base_api):
    return exception_decorator.ExceptionAwareApiCommunicator(
        base.ApiCommunicatorBase(base_api)
    )
