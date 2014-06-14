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
             additional_queries=(), binary=False):
        self.send_command(path, command, arguments, queries,
                          additional_queries=additional_queries)
        return self._get_receiver(binary).receive_synchronous()

    def call_async(self, path, command, arguments=None, queries=None,
                   additional_queries=(), binary=False):
        tag = self._get_next_tag()
        self.send_command(path, command, arguments, queries, tag=tag,
                          additional_queries=additional_queries)
        return ResponsePromise(self._get_receiver(binary), tag)

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

    def receive_single_response(self, binary=False):
        return self._get_receiver(binary).receive_single_response()

    def _get_next_tag(self):
        self.tag += 1
        return str(self.tag)

    def _get_receiver(self, binary):
        if binary:
            return ApiReceiver(self.base, self.response_buffor)
        else:
            return AsciiApiReceiver(self.base, self.response_buffor)


class ApiReceiver(object):
    sentence_class = sentence.ResponseSentence

    def __init__(self, base, response_buffor):
        self.base = base
        self.response_buffor = response_buffor

    def receive_single_response(self):
        serialized = []
        while not serialized:
            serialized = self.base.receive_sentence()
        response = self.sentence_class.parse(serialized)
        return response

    def process_single_response(self):
        response = self.receive_single_response()
        tag = response.tag if response.tag is not None else 'synchronous'
        asynchronous_response = self.response_buffor[tag]
        if response.type == 're':
            attributes = response.attributes
            asynchronous_response.attributes.append(attributes)
        elif response.type == 'done':
            asynchronous_response.done = True
        elif response.type == 'trap':
            asynchronous_response.done = True
            asynchronous_response.error = response.attributes['message']
        else:
            del(self.response_buffor[tag])
            raise exceptions.RouterOsApiConnectionClosedError(
                response.attributes['message'])

    def receive_synchronous(self):
        return self.receive_asynchronous('synchronous')

    def receive_asynchronous(self, tag):
        response = self.response_buffor[tag]
        while(not response.done):
            self.process_single_response()
        del(self.response_buffor[tag])
        if response.error:
            raise exceptions.RouterOsApiCommunicationError(response.error)
        else:
            return response.attributes


class AsciiApiReceiver(ApiReceiver):
    sentence_class = sentence.AsciiResponseSentence


class AsynchronousResponse(object):
    def __init__(self):
        self.attributes = []
        self.done = False
        self.error = None


class ResponsePromise(object):
    def __init__(self, receiver, tag):
        self.receiver = receiver
        self.tag = tag

    def get(self):
        return self.receiver.receive_asynchronous(self.tag)
