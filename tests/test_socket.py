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


class TestGetSocket(TestCase):
    @mock.patch('socket.socket.connect')
    def test_with_interrupt(self, connect):
        connect.side_effect = [
            socket.error(api_socket.EINTR),
            None
        ]
        api_socket.get_socket('host', 123)
        connect.assert_has_calls([mock.call(('host', 123)),
                                  mock.call(('host', 123))])

    @mock.patch('socket.socket.connect')
    def test_with_other_error(self, connect):
        connect.side_effect = [
            socket.error(1),
            None
        ]
        self.assertRaises(socket.error, api_socket.get_socket, 'host', 123)
        connect.assert_has_calls([mock.call(('host', 123))])
