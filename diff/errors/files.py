from pathlib import Path


class NotADirectoryException(Exception):

    _MESSAGE_TEMPLATE = 'The [{}] path does not point a directory. Please check the path and try again: [{}]'

    def __init__(self, path_name: str, path: Path):
        super().__init__(NotADirectoryException._MESSAGE_TEMPLATE.format(path_name, path))


class NotAFileException(Exception):

    _MESSAGE_TEMPLATE = 'The path [{}] does not point to a file. Please check the path and try again: [{}]'

    def __init__(self, path_name: str, path: Path):
        super().__init__(NotAFileException._MESSAGE_TEMPLATE.format(path_name, path))
