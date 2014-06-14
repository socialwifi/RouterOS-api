import collections

from routeros_api import exceptions
from routeros_api import sentence
from routeros_api import query


class ApiCommunicator(object):
    def __init__(self, base):
        self.base = base
        self.tag = 0
        self.response_buffor = collections.defaultdict(AsynchronousResponse)

    def call(self, path, command, arguments=None, queries=None,
             additional_queries=()):
        self.send_command(path, command, arguments, queries,
                          additional_queries=additional_queries)
        return self.receive_synchronous()

    def call_async(self, path, command, arguments=None, queries=None,
                   additional_queries=()):
        tag = self._get_next_tag()
        self.send_command(path, command, arguments, queries, tag=tag,
                          additional_queries=additional_queries)
        return ResponsePromise(self, tag)

    def send_command(self, path, command, arguments=None, queries=None,
                     tag=None, additional_queries=()):
        arguments = arguments or {}
        queries = queries or {}
        command = sentence.CommandSentence(path, command, tag=tag)
        for key, value in arguments.items():
            command.set(key, value)
        for key, value in queries.items():
            command.filter(query.IsEqualQuery(key, value))
        for additional_query in additional_queries:
            command.filter(additional_query)
        self.base.send_sentence(command.get_api_format())

    def receive_single_response(self):
        serialized = []
        while not serialized:
            serialized = self.base.receive_sentence()
        response = sentence.ResponseSentence.parse(serialized)
        return response

    def process_single_response(self):
        response = self.receive_single_response()
        tag = response.tag if response.tag is not None else b'synchronous'
        asynchronous_response = self.response_buffor[tag]
        if response.type == b're':
            attributes = response.attributes
            asynchronous_response.attributes.append(attributes)
        elif response.type == b'done':
            asynchronous_response.done = True
        elif response.type == b'trap':
            asynchronous_response.done = True
            asynchronous_response.error = response.attributes[b'message']
        else:
            del(self.response_buffor[tag])
            raise exceptions.RouterOsApiConnectionClosedError(
                response.attributes[b'message'])

    def receive_synchronous(self):
        return self.receive_asynchronous(b'synchronous')

    def receive_asynchronous(self, tag):
        response = self.response_buffor[tag]
        while(not response.done):
            self.process_single_response()
        del(self.response_buffor[tag])
        if response.error:
            raise exceptions.RouterOsApiCommunicationError(response.error)
        else:
            return response.attributes

    def _get_next_tag(self):
        self.tag += 1
        return str(self.tag).encode()


class AsynchronousResponse(object):
    def __init__(self):
        self.attributes = []
        self.done = False
        self.error = None


class ResponsePromise(object):
    def __init__(self, communicator, tag):
        self.communicator = communicator
        self.tag = tag

    def get(self):
        return self.communicator.receive_asynchronous(self.tag)
