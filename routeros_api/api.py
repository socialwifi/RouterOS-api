import hashlib
import binascii
from routeros_api import api_communicator
from routeros_api import communication_exception_parsers
from routeros_api import api_socket
from routeros_api import api_structure
from routeros_api import base_api
from routeros_api import exceptions
from routeros_api import resource


def connect(host, username='admin', password='', port=8728, ca_cert=None):
    return RouterOsApiPool(host, username, password, port, ca_cert).get_api()


class RouterOsApiPool(object):
    socket_timeout = 15.

    def __init__(self, host, username='admin', password='', port=8728, ca_cert=None):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.ca_cert = None
        self.connected = False
        self.socket = api_socket.DummySocket()
        self.communication_exception_parser = (
            communication_exception_parsers.ExceptionHandler())

    def get_api(self):
        if not self.connected:
            self.socket = api_socket.get_socket(self.host, self.port,
                                                timeout=self.socket_timeout, ca_cert=self.ca_cert)
            base = base_api.Connection(self.socket)
            communicator = api_communicator.ApiCommunicator(base)
            self.api = RouterOsApi(communicator)
            for handler in self._get_exception_handlers():
                communicator.add_exception_handler(handler)
            self.api.login(self.username, self.password)
            self.connected = True
        return self.api

    def disconnect(self):
        self.connected = False
        self.socket.close()
        self.socket = api_socket.DummySocket()

    def set_timeout(self, socket_timeout):
        self.socket_timeout = socket_timeout
        self.socket.settimeout(socket_timeout)

    def _get_exception_handlers(self):
        yield CloseConnectionExceptionHandler(self)
        yield self.communication_exception_parser


class RouterOsApi(object):
    def __init__(self, communicator):
        self.communicator = communicator

    def login(self, login, password):
        response = self.get_binary_resource('/').call('login')
        token = binascii.unhexlify(response.done_message['ret'])
        hasher = hashlib.md5()
        hasher.update(b'\x00')
        hasher.update(password.encode())
        hasher.update(token)
        hashed = b'00' + hasher.hexdigest().encode('ascii')
        self.get_binary_resource('/').call(
            'login', {'name': login.encode(), 'response': hashed})

    def get_resource(self, path, structure=None):
        structure = structure or api_structure.default_structure
        return resource.RouterOsResource(self.communicator, path, structure)

    def get_binary_resource(self, path):
        return resource.RouterOsBinaryResource(self.communicator, path)


class CloseConnectionExceptionHandler:
    def __init__(self, pool):
        self.pool = pool

    def handle(self, exception):
        connection_closed = isinstance(
            exception, exceptions.RouterOsApiConnectionError)
        fatal_error = isinstance(exception, exceptions.FatalRouterOsApiError)
        if connection_closed or fatal_error:
            self.pool.disconnect()
