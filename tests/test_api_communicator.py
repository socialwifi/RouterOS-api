from unittest import TestCase

try:
    from unittest import mock
except ImportError:
    import mock

from routeros_api import api_communicator
from routeros_api import exceptions


class TestCommunicator(TestCase):
    def test_login_call(self):
        base = mock.Mock()
        base.receive_sentence.return_value = [b'!done', b'=ret=some-hex',
                                              b'.tag=1']
        communicator = api_communicator.ApiCommunicator(base)
        response = communicator.call('/', 'login').get()
        self.assertEqual(response.done_message['ret'], b'some-hex')

    def test_normal_call(self):
        base = mock.Mock()
        base.receive_sentence.side_effect = [[b'!re', b'=x=y', b'.tag=1'],
                                             [b'!done', b'.tag=1']]
        communicator = api_communicator.ApiCommunicator(base)
        response = communicator.call('/interface/', 'print').get()
        self.assertEqual(response, [{'x': b'y'}])

    def test_mixed_calls(self):
        base = mock.Mock()
        base.receive_sentence.side_effect = [[b'!re', b'=x1=y1', b'.tag=1'],
                                             [b'!re', b'=x2=y2', b'.tag=2'],
                                             [b'!done', b'.tag=1'],
                                             [b'!done', b'.tag=2']]
        communicator = api_communicator.ApiCommunicator(base)
        promise = communicator.call('/interface/', 'print')
        response2 = communicator.call('/interface/', 'print').get()
        response1 = promise.get()
        self.assertEqual(response1, [{'x1': b'y1'}])
        self.assertEqual(response2, [{'x2': b'y2'}])

    def test_error_call(self):
        base = mock.Mock()
        base.receive_sentence.side_effect = [[b'!trap', b'=message=y',
                                              b'.tag=1'],
                                             [b'!done', b'.tag=1']]
        communicator = api_communicator.ApiCommunicator(base)
        promise = communicator.call('/file/', 'print')
        self.assertRaises(exceptions.RouterOsApiCommunicationError,
                          promise.get)

    def test_empty_call(self):
        base = mock.Mock()
        base.receive_sentence.side_effect = [[b'!empty', b'.tag=1'],
                                             [b'!done', b'.tag=1']]
        communicator = api_communicator.ApiCommunicator(base)
        response = communicator.call('/file/', 'print').get()
        self.assertEqual(response, [])

    def test_query_call(self):
        base = mock.Mock()
        base.receive_sentence.return_value = [b'!done', b'.tag=1']
        communicator = api_communicator.ApiCommunicator(base)
        communicator.call('/interface/', 'print', queries={'x': 'y'}).get()
        base.send_sentence.assert_called_once_with(
            [b'/interface/print', b'?x=y', b'.tag=1'])

    def test_set_call(self):
        base = mock.Mock()
        base.receive_sentence.return_value = [b'!done', b'.tag=1']
        communicator = api_communicator.ApiCommunicator(base)
        communicator.call('/interface/', 'set', {'x': b'y'})
        base.send_sentence.assert_called_once_with(
            [b'/interface/set', b'=x=y', b'.tag=1'])

    def test_call_with_arguments(self):
        base = mock.Mock()
        base.receive_sentence.return_value = [b'!done', b'.tag=1']
        communicator = api_communicator.ApiCommunicator(base)
        communicator.call('/interface/monitor-traffic/', 'monitor', {'interface': 'ether1'})
        base.send_sentence.assert_called_once_with(
            [b'/interface/monitor-traffic/monitor', b'=interface=ether1', b'.tag=1'])

    def test_call_without_arguments(self):
        base = mock.Mock()
        base.receive_sentence.return_value = [b'!done', b'.tag=1']
        communicator = api_communicator.ApiCommunicator(base)
        communicator.call('/interface/monitor-traffic/', 'monitor', {'once': None})
        base.send_sentence.assert_called_once_with(
            [b'/interface/monitor-traffic/monitor', b'=once', b'.tag=1'])

    def test_async_error_raises_when_synchronizing(self):
        base = mock.Mock()
        base.receive_sentence.side_effect = [
            [b'!trap', b'=message=m', b'.tag=1'],
            [b'!done', b'.tag=2'],
            [b'!done', b'.tag=1']]
        communicator = api_communicator.ApiCommunicator(base)
        promise = communicator.call('/interface/', 'print')
        communicator.call('/interface/', 'print').get()
        self.assertRaises(exceptions.RouterOsApiCommunicationError,
                          promise.get)
