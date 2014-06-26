from routeros_api import exceptions
from routeros_api import sentence
from routeros_api import query


class ApiCommunicator(object):
    def __init__(self, base):
        self.base = base
        self.tag = 0
        self.response_buffor = {}

    def call(self, path, command, arguments=None, queries=None,
             additional_queries=(), binary=False, include_done=False):
        command = self.get_command(path, command, arguments, queries,
                                   additional_queries=additional_queries)
        self.send_command(command)
        self.response_buffor['synchronous'] = AsynchronousResponse(
            command, binary, include_done)
        return self.receive_synchronous()

    def call_async(self, path, command, arguments=None, queries=None,
                   additional_queries=(), binary=False, include_done=False):
        tag = self._get_next_tag()
        command = self.get_command(path, command, arguments, queries, tag=tag,
                                   additional_queries=additional_queries)
        self.send_command(command)
        self.response_buffor[tag] = AsynchronousResponse(
            command, binary, include_done)
        return ResponsePromise(self, tag)

    def get_command(self, path, command, arguments=None, queries=None,
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
        return command

    def send_command(self, command):
        self.base.send_sentence(command.get_api_format())

    def _get_next_tag(self):
        self.tag += 1
        return str(self.tag)

    def receive_single_response(self):
        serialized = []
        while not serialized:
            serialized = self.base.receive_sentence()
        response = sentence.ResponseSentence.parse(serialized)
        return response

    def process_single_response(self):
        response = self.receive_single_response()
        tag = response.tag if response.tag is not None else 'synchronous'
        asynchronous_response = self.response_buffor[tag]
        if response.type in asynchronous_response.get_meaningfull_responses():
            attributes = response.attributes
            asynchronous_response.attributes.append(attributes)
        if response.type == 'done':
            asynchronous_response.done = True
        elif response.type == 'trap':
            asynchronous_response.error = response.attributes['message']
        elif response.type == 'fatal':
            del(self.response_buffor[tag])
            message = "Fatal error executing command {}".format(
                asynchronous_response.command)
            raise exceptions.RouterOsApiConnectionClosedError(message)

    def receive_synchronous(self):
        return self.receive_asynchronous('synchronous')

    def receive_asynchronous(self, tag):
        response = self.response_buffor[tag]
        while(not response.done):
            self.process_single_response()
        del(self.response_buffor[tag])
        if response.error:
            message = "Error \"{}\" executing command {}".format(
                response.error.decode(), response.command)
            raise exceptions.RouterOsApiCommunicationError(message)
        else:
            if not response.binary:
                response.decode()
            return response.attributes


class AsynchronousResponse(object):
    def __init__(self, command, binary, include_done):
        self.attributes = []
        self.done = False
        self.error = None
        self.command = command
        self.binary = binary
        self.include_done = include_done

    def decode(self):
        for attribute in self.attributes:
            for key in attribute:
                attribute[key] = attribute[key].decode()

    def get_meaningfull_responses(self):
        if self.include_done:
            save_responses = ['re', 'done']
        else:
            save_responses = ['re']
        return save_responses


class ResponsePromise(object):
    def __init__(self, receiver, tag):
        self.receiver = receiver
        self.tag = tag

    def get(self):
        return self.receiver.receive_asynchronous(self.tag)
