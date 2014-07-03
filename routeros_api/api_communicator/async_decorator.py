class AsyncApiCommunicator(object):
    def __init__(self, inner):
        self.inner = inner

    def call(self, *args, **kwargs):
        tag = self.inner.send(*args, **kwargs)
        return ResponsePromise(self.inner, tag)

class ResponsePromise(object):
    def __init__(self, receiver, tag):
        self.receiver = receiver
        self.tag = tag

    def get(self):
        return self.receiver.receive(self.tag)
