from unittest import TestCase

try:
    from unitetest import mock
except ImportError:
    import mock

from routeros_api import exceptions
from routeros_api import api_communicator

class TestResponseSentence(TestCase):
    def test_login_call(self):
        base = mock.Mock()
        base.receive_sentence.return_value = [b'!done', b'=ret=some-hex']
        communicator = api_communicator.ApiCommunicator(base)
        response = communicator.call('/', 'login', include_done=True)
        self.assertEqual(response[0]['ret'], 'some-hex')

    def test_normal_call(self):
        base = mock.Mock()
        base.receive_sentence.side_effect = [[b'!re', b'=x=y'],[b'!done']]
        communicator = api_communicator.ApiCommunicator(base)
        response = communicator.call('/interface/', 'print')
        self.assertEqual(response, [{'x': 'y'}])

    def test_async_call(self):
        base = mock.Mock()
        base.receive_sentence.side_effect = [[b'!re', b'=x=y', b'.tag=1'],
                                             [b'!done', b'.tag=1']]
        communicator = api_communicator.ApiCommunicator(base)
        promise = communicator.call_async('/interface/', 'print')
        response = promise.get()
        self.assertEqual(response, [{'x': 'y'}])

    def test_mixed_calls(self):
        base = mock.Mock()
        base.receive_sentence.side_effect = [[b'!re', b'=x1=y1', b'.tag=1'],
                                             [b'!re', b'=x2=y2',],
                                             [b'!done', b'.tag=1'],
                                             [b'!done']]
        communicator = api_communicator.ApiCommunicator(base)
        promise = communicator.call_async('/interface/', 'print')
        response2 = communicator.call('/interface/', 'print')
        response1 = promise.get()
        self.assertEqual(response1, [{'x1': 'y1'}])
        self.assertEqual(response2, [{'x2': 'y2'}])

    def test_binary_call(self):
        base = mock.Mock()
        base.receive_sentence.side_effect = [[b'!re', b'=x=y', b'.tag=1'],
                                             [b'!done', b'.tag=1']]
        communicator = api_communicator.ApiCommunicator(base)
        promise = communicator.call_async('/file/', 'print', binary=True)
        response = promise.get()
        self.assertEqual(response, [{'x': b'y'}])

    def test_error_call(self):
        base = mock.Mock()
        base.receive_sentence.side_effect = [[b'!trap', b'=message=y'],
                                             [b'!done']]
        communicator = api_communicator.ApiCommunicator(base)
        self.assertRaises(exceptions.RouterOsApiCommunicationError,
                          communicator.call, '/file/', 'print')

    def test_query_call(self):
        base = mock.Mock()
        base.receive_sentence.return_value = [b'!done']
        communicator = api_communicator.ApiCommunicator(base)
        communicator.call('/interface/', 'print', queries={'x': 'y'})
        base.send_sentence.assert_called_once_with(
            [b'/interface/print', b'?x=y'])

    def test_set_call(self):
        base = mock.Mock()
        base.receive_sentence.return_value = [b'!done']
        communicator = api_communicator.ApiCommunicator(base)
        communicator.call('/interface/', 'set', {'x': 'y'})
        base.send_sentence.assert_called_once_with(
            [b'/interface/set', b'=x=y'])

    def test_async_error_raises_when_synchronizing(self):
        base = mock.Mock()
        base.receive_sentence.side_effect = [
            [b'!trap', b'=message=m', b'.tag=1'],
            [b'!done', b'.tag=1'],
            [b'!done']]
        communicator = api_communicator.ApiCommunicator(base)
        promise = communicator.call_async('/interface/', 'print')
        communicator.call('/interface/', 'print')
        self.assertRaises(exceptions.RouterOsApiCommunicationError,
                          promise.get)

    def test_mixed_binary_and_ascii_calls(self):
        base = mock.Mock()
        base.receive_sentence.side_effect = [[b'!re', b'=x1=y1', b'.tag=1'],
                                             [b'!re', b'=x2=y2',],
                                             [b'!done', b'.tag=1'],
                                             [b'!done']]
        communicator = api_communicator.ApiCommunicator(base)
        promise = communicator.call_async('/interface/', 'print', binary=True)
        response2 = communicator.call('/interface/', 'print')
        response1 = promise.get()
        self.assertEqual(response1, [{'x1': b'y1'}])
        self.assertEqual(response2, [{'x2': 'y2'}])
