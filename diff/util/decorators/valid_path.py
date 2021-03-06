from pathlib import Path
import enum


class PathType(enum.Enum):
    Directory = 0
    File = 1


def _validate_path(path: Path, validation_type: PathType):
    if validation_type == PathType.Directory and not path.is_dir():
        raise Exception(f'The path [{path}] either does not exist or does not point to a directory.')
    elif validation_type == PathType.File and not path.is_file():
        raise Exception(f'The path [{path}] either does not exist or does not point to a file.')


def valid_path(*validation_type: PathType):
    def inner(function):
        def wrapper(*arguments):
            current_validation = 0
            processed_arguments = []
            for argument in arguments:
                if type(argument) is str and current_validation < len(validation_type):
                    current_validation_type = validation_type[current_validation]
                    current_validation = current_validation + 1
                    path = Path(argument)
                    _validate_path(path, current_validation_type)
                    processed_arguments.append(path)
                else:
                    processed_arguments.append(argument)
            return function(*processed_arguments)
        return wrapper
    return inner
