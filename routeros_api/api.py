import hashlib
import binascii
from routeros_api import api_communicator
from routeros_api import api_socket
from routeros_api import base_api
from routeros_api import resource
from routeros_api import api_structure


def connect(host, username='admin', password='', port=8728):
    socket = api_socket.get_socket(host, port)
    base = base_api.Connection(socket)
    close_handler = api_socket.CloseConnectionExceptionHandler(socket)
    communicator = api_communicator.ApiCommunicator(base)
    communicator.add_exception_handler(close_handler)
    api = RouterOsApi(communicator, socket)
    api.login(username, password)
    return api


class RouterOsApi(object):
    def __init__(self, communicator, socket):
        self.communicator = communicator
        self.socket = socket

    def login(self, login, password):
        response = self.get_binary_resource('/').call(
            'login')
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

    def close(self):
        self.socket.close()
