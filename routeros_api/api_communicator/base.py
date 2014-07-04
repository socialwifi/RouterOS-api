from routeros_api import exceptions
from routeros_api import sentence
from routeros_api import query


class ApiCommunicatorBase(object):
    def __init__(self, base):
        self.base = base
        self.tag = 0
        self.response_buffor = {}

    def send(self, path, command, arguments=None, queries=None,
                   additional_queries=(), include_done=False):
        tag = self._get_next_tag()
        command = self.get_command(path, command, arguments, queries, tag=tag,
                                   additional_queries=additional_queries)
        self.send_command(command)
        self.response_buffor[tag] = AsynchronousResponse(
            command, include_done)
        return tag

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
        return str(self.tag).encode()

    def receive(self, tag):
        response = self.response_buffor[tag]
        while(not response.done):
            self.process_single_response()
        del(self.response_buffor[tag])
        if response.error:
            message = "Error \"{error}\" executing command {command}".format(
                error=response.error.decode(), command=response.command)
            raise exceptions.RouterOsApiCommunicationError(message)
        else:
            return response.attributes

    def process_single_response(self):
        response = self.receive_single_response()
        if response.tag not in self.response_buffor:
            raise exceptions.FatalRouterOsApiError(
                "Unknown tag %s", response.tag)
        asynchronous_response = self.response_buffor[response.tag]
        if response.type in asynchronous_response.get_meaningfull_responses():
            attributes = response.attributes
            asynchronous_response.attributes.append(attributes)
        if response.type == b'done':
            asynchronous_response.done = True
        elif response.type == b'trap':
            asynchronous_response.error = response.attributes[b'message']
        elif response.type == b'fatal':
            del(self.response_buffor[response.tag])
            message = "Fatal error executing command {command}".format(
                command=asynchronous_response.command)
            raise exceptions.RouterOsApiConnectionClosedError(message)

    def receive_single_response(self):
        serialized = []
        while not serialized:
            serialized = self.base.receive_sentence()
        response = sentence.ResponseSentence.parse(serialized)
        return response


class AsynchronousResponse(object):
    def __init__(self, command, include_done):
        self.attributes = []
        self.done = False
        self.error = None
        self.command = command
        self.include_done = include_done

    def get_meaningfull_responses(self):
        if self.include_done:
            save_responses = [b're', b'done']
        else:
            save_responses = [b're']
        return save_responses
