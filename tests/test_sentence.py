from unittest import TestCase

from routeros_api import exceptions
from routeros_api import sentence


class TestResponseSentence(TestCase):
    def test_done(self):
        response = sentence.ResponseSentence.parse([b'!done'])
        self.assertEqual(response.type, b'done')

    def test_simple_re(self):
        response = sentence.ResponseSentence.parse([b'!re'])
        self.assertEqual(response.type, b're')

    def test_re_with_attributes(self):
        response = sentence.ResponseSentence.parse([b'!re', b'=a=b'])
        self.assertEqual(response.attributes[b'a'], b'b')

    def test_re_with_tag(self):
        response = sentence.ResponseSentence.parse([b'!re', b'.tag=b'])
        self.assertEqual(response.tag, b'b')

    def test_re_with_invalid_word(self):
        self.assertRaises(exceptions.RouterOsApiParsingError,
                          sentence.ResponseSentence.parse, [b'!re', b'?tag=b'])

    def test_trap(self):
        response = sentence.ResponseSentence.parse([b'!trap', b'=message=b'])
        self.assertEqual(response.type, b'trap')
        self.assertEqual(response.attributes[b'message'], b'b')


class TestCommandSentence(TestCase):
    def test_login_sentence(self):
        command = sentence.CommandSentence(b'/', b'login')
        command.set(b'username', b'admin')
        self.assertEqual(command.get_api_format(),
                         [b'/login', b'=username=admin'])

    def test_query_sentence(self):
        command = sentence.CommandSentence(b'/interface/', b'print')
        command.filter(name=b'wlan0')
        self.assertEqual(command.get_api_format(),
                         [b'/interface/print', b'?name=wlan0'])

    def test_query_sentence_with_tag(self):
        command = sentence.CommandSentence(b'/interface/', b'print', tag=b'0')
        command.filter(name=b'wlan0')
        self.assertEqual(command.get_api_format(),
                         [b'/interface/print', b'?name=wlan0', b'.tag=0'])
