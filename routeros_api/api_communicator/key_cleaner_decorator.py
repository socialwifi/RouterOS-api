class KeyCleanerApiCommunicator(object):
    def __init__(self, inner):
        self.inner = inner

    def send(self, path, command, arguments=None, queries=None,
             additional_queries=(), include_done=False):
        encoded_arguments = encode_dictionary(arguments or {})
        encoded_queries = encode_dictionary(queries or {})
        return self.inner.send(
            path, command, arguments=encoded_arguments,
            queries=encoded_queries, additional_queries=additional_queries,
            include_done=include_done)

    def receive(self, tag):
        answers = self.inner.receive(tag)
        return [decode_dictionary(answer) for answer in answers]


def encode_dictionary(dictionary):
    return dict([(encode_key(key), value) for key, value in
                 dictionary.items()])


def encode_key(key):
    key = key.replace(b'_', b'-')
    if key in [b'id', b'proplist']:
        return b'.' + key
    else:
        return key

def decode_dictionary(dictionary):
    return dict([(decode_key(key), value) for key, value in
                 dictionary.items()])


def decode_key(key):
    if key in [b'.id', b'.proplist']:
        return key[1:]
    else:
        return key
