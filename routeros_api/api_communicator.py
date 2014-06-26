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
             additional_queries=(), binary=False, include_done=False):
        self.send_command(path, command, arguments, queries,
                          additional_queries=additional_queries)
        return self._get_receiver(binary, include_done).receive_synchronous()

    def call_async(self, path, command, arguments=None, queries=None,
                   additional_queries=(), binary=False, include_done=False):
        tag = self._get_next_tag()
        self.send_command(path, command, arguments, queries, tag=tag,
                          additional_queries=additional_queries)
        return ResponsePromise(self._get_receiver(binary, include_done), tag)

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

    def _get_next_tag(self):
        self.tag += 1
        return str(self.tag)

    def _get_receiver(self, binary, include_done):
        if binary:
            sentence_class = sentence.ResponseSentence
        else:
            sentence_class = sentence.AsciiResponseSentence

        if include_done:
            save_responses = ['re', 'done']
        else:
            save_responses = ['re']
        return ApiReceiver(self.base, self.response_buffor, sentence_class,
                           save_responses)


class ApiReceiver(object):
    def __init__(self, base, response_buffor, sentence_class, save_responses):
        self.base = base
        self.response_buffor = response_buffor
        self.sentence_class = sentence_class
        self.save_responses = save_responses

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
        if response.type in self.save_responses:
            attributes = response.attributes
            asynchronous_response.attributes.append(attributes)
        if response.type == 'done':
            asynchronous_response.done = True
        elif response.type == 'trap':
            asynchronous_response.done = True
            asynchronous_response.error = response.attributes['message']
        elif response.type == 'fatal':
            del(self.response_buffor[tag])
            raise exceptions.RouterOsApiConnectionClosedError()

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
