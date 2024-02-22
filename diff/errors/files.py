from pathlib import Path


class MissingPathException(Exception):

    _MESSAGE_TEMPLATE = 'The path argument [{}] does not point to a {}. Please check the path and try again: [{}]'

    def __init__(self, path_type: str, path_name: str, path: Path):
        super().__init__(MissingPathException._MESSAGE_TEMPLATE.format(path_name, path_type, path))


class NotADirectoryException(MissingPathException):

    def __init__(self, path_name: str, path: Path):
        super().__init__('directory', path_name, path)


class NotAFileException(Exception):

    def __init__(self, path_name: str, path: Path):
        super().__init__('file', path_name, path)
