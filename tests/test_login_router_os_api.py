import unittest

from routeros_api import api
from routeros_api import api_communicator
from routeros_api import base_api

try:
    from unittest import mock
except ImportError:
    import mock


class TestLoginRouterOsApi(unittest.TestCase):
    def get_api(self):
        socket = mock.MagicMock()
        base = base_api.Connection(socket)
        base.receive_sentence = mock.Mock(return_value=[b'!done', b'.tag=1'])
        communicator = api_communicator.ApiCommunicator(base)
        routeros_api = api.RouterOsApi(communicator)
        return routeros_api

    def test_login(self):
        routeros_api = self.get_api()
        routeros_api.login('admin', 'password123', plaintext_login=False)

    def test_plain_text_login(self):
        routeros_api = self.get_api()
        routeros_api.login('admin', 'password123', plaintext_login=True)

    def test_plain_text_login_with_bytes(self):
        routeros_api = self.get_api()
        routeros_api.login(b'admin', b'password123', plaintext_login=True)
