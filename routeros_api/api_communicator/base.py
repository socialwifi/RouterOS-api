from routeros_api import exceptions
from routeros_api import query
from routeros_api import sentence


class ApiCommunicatorBase(object):
    def __init__(self, base):
        self.base = base
        self.tag = 0
        self.response_buffor = {}

    def send(self, path, command, arguments=None, queries=None, additional_queries=()):
        tag = self._get_next_tag()
        command = self.get_command(path, command, arguments, queries, tag=tag, additional_queries=additional_queries)
        self.send_command(command)
        self.response_buffor[tag] = AsynchronousResponse(command=command)
        return tag

    def get_command(self, path, command, arguments=None, queries=None, tag=None, additional_queries=()):
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
        response_buffor_manager = AsynchronousResponseBufforManager(self, tag)
        while not response_buffor_manager.done:
            response_buffor_manager.step_to_finish_response()
        response_buffor_manager.clean()
        response = response_buffor_manager.response
        if response.error:
            raise response.error_as_exception
        else:
            return response

    def receive_iterator(self, tag):
        response_buffor_manager = AsynchronousResponseBufforManager(self, tag)
        return AsynchronousResponseIterator(response_buffor_manager)

    def process_single_response(self):
        response = self.receive_single_response()
        response.save_to_buffor(self.response_buffor)

    def receive_single_response(self):
        serialized = []
        while not serialized:
            serialized = self.base.receive_sentence()
        response_sentence = sentence.ResponseSentence.parse(serialized)
        return SingleResponse(response_sentence)


class SingleResponse(object):
    def __init__(self, response_sentence):
        self.response = response_sentence

    def save_to_buffor(self, buffor):
        if self.response.tag not in buffor:
            raise exceptions.FatalRouterOsApiError(
                "Unknown tag %s", self.response.tag)
        asynchronous_response = buffor[self.response.tag]
        if self.response.type == b're':
            attributes = self.response.attributes
            asynchronous_response.append(attributes)
        if self.response.type == b'done':
            asynchronous_response.done = True
            attributes = self.response.attributes
            asynchronous_response.done_message = attributes
        elif self.response.type == b'trap':
            asynchronous_response.error = self.response.attributes[b'message']
        elif self.response.type == b'fatal':
            del (buffor[self.response.tag])
            message = "Fatal error executing command {command}".format(
                command=asynchronous_response.command)
            raise exceptions.RouterOsApiFatalCommunicationError(message)


class AsynchronousResponseIterator:
    def __init__(self, response_buffor_manager):
        self.response_buffor_manager = response_buffor_manager
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        response = self.response_buffor_manager.response
        while self.end_of_buffered and not self.response_buffor_manager.done:
            self.response_buffor_manager.step_to_finish_response()
        if self.end_of_buffered and response.error:
            self.response_buffor_manager.clean()
            raise response.error_as_exception
        elif self.end_of_buffered:
            self.response_buffor_manager.clean()
            raise StopIteration
        else:
            current = response[self.index]
            self.index += 1
            return current

    @property
    def end_of_buffered(self):
        return self.index >= len(self.response_buffor_manager.response)


class AsynchronousResponseBufforManager(object):
    def __init__(self, receiver, tag):
        self.receiver = receiver
        self.tag = tag
        self.response = self.receiver.response_buffor[self.tag]

    def step_to_finish_response(self):
        self.receiver.process_single_response()

    @property
    def done(self):
        return self.response.done

    def clean(self):
        del (self.receiver.response_buffor[self.tag])


class AsynchronousResponse(list):
    def __init__(self, *args, **kwargs):
        self.command = kwargs.pop('command')
        super(AsynchronousResponse, self).__init__(*args, **kwargs)
        self.done_message = {}
        self.done = False
        self.error = None

    @property
    def error_as_exception(self):
        if self.error:
            message = "Error \"{error}\" executing command {command}".format(
                error=self.error.decode(),
                command=self.command)
            return exceptions.RouterOsApiCommunicationError(
                message, self.error)
        else:
            return None

    def map(self, function):
        result = type(self)(map(function, self), command=self.command)
        result.done_message = function(self.done_message)
        result.done = self.done
        result.error = self.error
        return result
