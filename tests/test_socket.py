import socket

from unittest import TestCase

try:
    from unittest import mock
except ImportError:
    import mock

from routeros_api import api_socket
from routeros_api import exceptions


class TestSocketWrapper(TestCase):
    def test_socket(self):
        inner = mock.Mock()
        wrapper = api_socket.SocketWrapper(inner)
        inner.recv.side_effect = [
            socket.error(api_socket.EINTR),
            'bytes',
        ]
        self.assertEqual(wrapper.receive(5), 'bytes')


class TestGetSocket(TestCase):
    @mock.patch('socket.create_connection')
    def test_with_interrupt(self, create_connection_mock):
        create_connection_mock.side_effect = [
            socket.error(api_socket.EINTR),
            mock.Mock(),
        ]
        api_socket.get_socket('host', 123)
        create_connection_mock.assert_has_calls([
            mock.call(('host', 123), timeout=15.0),
            mock.call(('host', 123), timeout=15.0),
        ])

    @mock.patch('socket.create_connection')
    def test_with_other_error(self, create_connection_mock):
        create_connection_mock.side_effect = [
            socket.error(1),
            None,
        ]
        self.assertRaises(exceptions.RouterOsApiConnectionError,
                          api_socket.get_socket, 'host', 123)
        create_connection_mock.assert_has_calls([
            mock.call(('host', 123), timeout=15.0),
        ])
