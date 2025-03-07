try:
    from unittest import mock
except ImportError:
    import mock

import unittest

from routeros_api import api_structure as structure
from routeros_api import resource
from routeros_api.api_communicator import base

STRING_STRUCTURE = {'string': structure.StringField()}
BYTES_STRUCTURE = {'bytes': structure.BytesField()}
BOOLEAN_STRUCTURE = {'boolean': structure.BooleanField()}


class TestTypedResource(unittest.TestCase):
    def test_unknown_resource_get(self):
        communicator = mock.Mock()
        response = base.AsynchronousResponse([{'x': b'y'}], command='')
        communicator.call.return_value.get.return_value = response
        some_resource = resource.RouterOsResource(communicator, '/unknown',
                                                  structure.default_structure)
        result = some_resource.get()
        self.assertEqual(result, [{'x': 'y'}])

    def test_unknown_resource_set(self):
        communicator = mock.Mock()
        some_resource = resource.RouterOsResource(communicator, '/unknown',
                                                  structure.default_structure)
        some_resource.set(x='y')
        communicator.call.assert_called_with(
            '/unknown/', 'set', arguments={'x': b'y'}, queries={},
            additional_queries=())

    def test_unknown_resource_set_with_no_value(self):
        communicator = mock.Mock()
        some_resource = resource.RouterOsResource(communicator, '/unknown',
                                                  structure.default_structure)
        some_resource.set(x=None)
        communicator.call.assert_called_with(
            '/unknown/', 'set', arguments={'x': None}, queries={},
            additional_queries=())

    def test_string_resource_get(self):
        communicator = mock.Mock()
        response = base.AsynchronousResponse([{'string': b's'}], command='')
        communicator.call.return_value.get.return_value = response
        some_resource = resource.RouterOsResource(communicator, '/string', STRING_STRUCTURE)
        result = some_resource.get()
        self.assertEqual(result, [{'string': 's'}])

    def test_string_resource_get_non_utf8_characters(self):
        communicator = mock.Mock()
        response = base.AsynchronousResponse([{'string': b'test-\xb9\xe6\xbf-test'}], command='')
        communicator.call.return_value.get.return_value = response
        some_resource = resource.RouterOsResource(communicator, '/string', STRING_STRUCTURE)
        result = some_resource.get()
        self.assertEqual(result, [{'string': 'test-\\xb9\\xe6\\xbf-test'}])

    def test_string_resource_get_windows_1250_characters(self):
        string_structure = {'string': structure.StringField(encoding='windows-1250')}
        communicator = mock.Mock()
        response = base.AsynchronousResponse([{'string': b'test-\xb9\xe6\xbf\x8f-test'}], command='')
        communicator.call.return_value.get.return_value = response
        some_resource = resource.RouterOsResource(communicator, '/string', string_structure)
        result = some_resource.get()
        self.assertEqual(result, [{'string': 'test-ąćżŹ-test'}])

    def test_string_resource_get_latin_1_characters(self):
        string_structure = {'string': structure.StringField(encoding='latin-1')}
        communicator = mock.Mock()
        response = base.AsynchronousResponse([{'string': b'hap ac\xb2'}], command='')
        communicator.call.return_value.get.return_value = response
        some_resource = resource.RouterOsResource(communicator, '/string', string_structure)
        result = some_resource.get()
        self.assertEqual(result, [{'string': 'hap ac²'}])

    def test_bytes_resource_get(self):
        communicator = mock.Mock()
        response = base.AsynchronousResponse([{'bytes': b'y'}], command='')
        communicator.call.return_value.get.return_value = response
        some_resource = resource.RouterOsResource(communicator, '/bytes',
                                                  BYTES_STRUCTURE)
        result = some_resource.get()
        self.assertEqual(result, [{'bytes': b'y'}])

    def test_bytes_resource_set(self):
        communicator = mock.Mock()
        some_resource = resource.RouterOsResource(communicator, '/bytes',
                                                  BYTES_STRUCTURE)
        some_resource.set(bytes=b'y')
        communicator.call.assert_called_with(
            '/bytes/', 'set', arguments={'bytes': b'y'}, queries={},
            additional_queries=())

    def test_boolean_resource_get(self):
        communicator = mock.Mock()
        response = base.AsynchronousResponse([{'boolean': b'yes'}], command='')
        communicator.call.return_value.get.return_value = response
        some_resource = resource.RouterOsResource(communicator, '/boolean',
                                                  BOOLEAN_STRUCTURE)
        result = some_resource.get()
        self.assertEqual(result, [{'boolean': True}])

    def test_boolean_resource_set(self):
        communicator = mock.Mock()
        some_resource = resource.RouterOsResource(communicator, '/boolean',
                                                  BOOLEAN_STRUCTURE)
        some_resource.set(boolean=True)
        communicator.call.assert_called_with(
            '/boolean/', 'set', arguments={'boolean': b'yes'}, queries={},
            additional_queries=())
