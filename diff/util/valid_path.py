from pathlib import Path


DIRECTORY = 0
FILE = 1


def _validate_path(path: Path, validation_type: int):
    if validation_type == DIRECTORY and not path.is_dir():
        raise Exception(f'The path [{path}] either does not exist or does not point to a directory.')
    elif validation_type == FILE and not path.is_file():
        raise Exception(f'The path [{path}] either does not exist or does not point to a file.')


def valid_path(validation_type: int):
    def inner(function):
        def wrapper(*arguments):
            processed_arguments = []
            for argument in arguments:
                if type(argument) is str:
                    path = Path(argument)
                    _validate_path(path, validation_type)
                    processed_arguments.append(path)
                else:
                    processed_arguments.append(argument)
            return function(*processed_arguments)
        return wrapper
    return inner