class AsyncApiCommunicator(object):
    def __init__(self, inner):
        self.inner = inner

    def call_async(self, path, command, arguments=None, queries=None,
                   additional_queries=(), include_done=False):
        tag = self.inner.send(path, command, arguments, queries,
                              additional_queries, include_done)
        return ResponsePromise(self.inner, tag)

class ResponsePromise(object):
    def __init__(self, receiver, tag):
        self.receiver = receiver
        self.tag = tag

    def get(self):
        return self.receiver.receive(self.tag)
