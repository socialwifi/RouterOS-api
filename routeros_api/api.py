import hashlib
import binascii
from routeros_api import api_communicator
from routeros_api import api_socket
from routeros_api import base_api


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
            'login', include_done=True)
        token = binascii.unhexlify(response[0]['ret'])
        hasher = hashlib.md5()
        hasher.update(b'\x00')
        hasher.update(password.encode())
        hasher.update(token)
        hashed = b'00' + hasher.hexdigest().encode('ascii')
        self.get_binary_resource('/').call(
            'login', {'name': login.encode(), 'response': hashed})

    def get_resource(self, path):
        return RouterOsResource(self.communicator, path)

    def get_binary_resource(self, path):
        return RouterOsResource(self.communicator, path, binary=True)

    def close(self):
        self.socket.close()


class RouterOsResource(object):
    def __init__(self, communicator, path, binary=False):
        self.communicator = communicator
        self.path = clean_path(path)
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
             additional_queries=(), include_done=False):
        return self.communicator.call(
            self.path, command, arguments=arguments, queries=queries,
            additional_queries=additional_queries, binary=self.binary,
            include_done=include_done).get()

    def call_async(self, command, arguments=None, queries=None,
             additional_queries=(), include_done=False):
        return self.communicator.call(
            self.path, command, arguments=arguments, queries=queries,
            additional_queries=additional_queries, binary=self.binary,
            include_done=include_done)

    def __repr__(self):
        return 'RouterOsResource({path}, {binary})'.format(path=self.path,
                                                           binary=self.binary)


def clean_path(path):
    if not path.endswith('/'):
        path += '/'
    if not path.startswith('/'):
        path = '/' + path
    return path
