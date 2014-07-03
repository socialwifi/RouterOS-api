class EncodingApiCommunicator(object):
    def __init__(self, inner):
        self.inner = inner

    def call(self, path, command, arguments=None, queries=None,
                   additional_queries=(), include_done=False, binary=False):
        queries = queries or {}
        path = path.encode()
        command = command.encode()
        arguments = self.encode_dictionary(arguments or {}, binary)
        queries = self.encode_dictionary(queries or {}, binary)
        promise = self.inner.call(
            path, command, arguments, queries, additional_queries,
            include_done)
        return EncodedPromiseDecorator(promise, binary)

    def encode_dictionary(self, dictionary, binary_values):
        encoded_arguments = {}
        for key, value in dictionary.items():
            if binary_values:
                encoded_arguments[key.encode()] = value
            else:
                encoded_arguments[key.encode()] = value.encode()
        return encoded_arguments


class EncodedPromiseDecorator(object):
    def __init__(self, inner, binary_values):
        self.inner = inner
        self.binary_values = binary_values

    def get(self):
        response = self.inner.get()
        decoded_response = []
        for row in response:
            decoded_row = self.decode_dictionary(row)
            decoded_response.append(decoded_row)
        return decoded_response

    def decode_dictionary(self, dictionary):
        decoded_dictionary = {}
        for key, value in dictionary.items():
            if self.binary_values:
                decoded_dictionary[key.decode()] = value
            else:
                decoded_dictionary[key.decode()] = value.decode()
        return decoded_dictionary
