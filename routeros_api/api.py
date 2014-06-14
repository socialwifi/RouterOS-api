import hashlib
import binascii
from routeros_api import api_communicator
from routeros_api import api_socket
from routeros_api import base_api


def connect(host, username='admin', password='', port=8728):
    socket = api_socket.get_socket(host, port)
    base = base_api.Connection(socket)
    communicator = api_communicator.ApiCommunicator(base)
    login(communicator, username, password)
    return RouterOsApi(communicator)

def login(communicator, login, password):
    communicator.send_command('/', 'login')
    response = communicator.receive_single_response()
    token = binascii.unhexlify(response.attributes['ret'])
    hasher = hashlib.md5()
    hasher.update(b'\x00')
    hasher.update(password.encode())
    hasher.update(token)
    hashed = b'00' + hasher.hexdigest().encode('ascii')
    communicator.call('/', 'login', {'name': login, 'response': hashed})

class RouterOsApi(object):
    def __init__(self, communicator):
        self.communicator = communicator

    def get_resource(self, path):
        return RouterOsResource(self.communicator, path)

    def get_binary_resource(self, path):
        return RouterOsResource(self.communicator, path, binary=True)

class RouterOsResource(object):
    def __init__(self, communicator, path, binary=False):
        self.communicator = communicator
        self.path = path
        self.binary = binary

    def get(self, **kwargs):
        return self.call('print', {}, kwargs)

    def get_async(self, **kwargs):
        return self.call_async('print', {}, kwargs)

    def detailed_get(self, **kwargs):
        return self.call('print', {'detail': ''}, kwargs)

    def detailed_get_async(self, **kwargs):
        return self.call_async('print', {'detail': ''}, kwargs)

    def set(self, **kwargs):
        return self.call('set', kwargs)

    def set_async(self, **kwargs):
        return self.call('set', kwargs)

    def add(self, **kwargs):
        return self.call('add', kwargs)

    def add_async(self, **kwargs):
        return self.call_async('add', kwargs)

    def remove(self, **kwargs):
        return self.call('remove', kwargs)

    def remove_async(self, **kwargs):
        return self.call_async('remove', kwargs)

    def call(self, command, arguments=None, queries=None,
             additional_queries=()):
        return self.communicator.call(
            self.path, command, arguments=arguments, queries=queries,
            additional_queries=additional_queries, binary=self.binary)

    def call_async(self, command, arguments=None, queries=None,
             additional_queries=()):
        return self.communicator.call_async(
            self.path, command, arguments=arguments, queries=queries,
            additional_queries=additional_queries, binary=self.binary)
