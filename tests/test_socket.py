import socket
from unittest import TestCase

try:
    from unitetest import mock
except ImportError:
    import mock

from routeros_api import api_socket

class TestSocketWrapper(TestCase):
    def test_socket(self):
        inner = mock.Mock()
        wrapper = api_socket.SocketWrapper(inner)
        inner.recv.side_effect = [
            socket.error(api_socket.EINTR),
            'bytes'
        ]
        self.assertEqual(wrapper.receive(5), 'bytes')
