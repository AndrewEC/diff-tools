class UnsupportedAlgorithmException(Exception):

    _MESSAGE_TEMPLATE = ('The specified checksum algorithm, [{}], does not appear to be available on this system. '
                         'Choose another hash algorithm and try again.')

    def __init__(self, algorithm_name: str):
        super().__init__(UnsupportedAlgorithmException._MESSAGE_TEMPLATE.format(algorithm_name))
