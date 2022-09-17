from typing import Tuple, Any
from pathlib import Path
import enum


class PathType(enum.Enum):
    """
    Specifies the string parameter should be parsed into a Path object and validated as a directory.
    """
    Directory = 0

    """
    Specifies the string parameter should be parsed into a Path object and validated as a file.
    """
    File = 1


class _ArgumentValidator:

    def __init__(self, validation_type: Tuple[PathType]):
        self._validation_type = validation_type
        self._last_validated_index = 0

    def augment_argument(self, argument: Any) -> Any:
        if not self._can_validate_argument(argument):
            return argument
        path = Path(argument)
        self._validate_path(path)
        return path

    def _can_validate_argument(self, argument: Any) -> bool:
        return self._last_validated_index < len(self._validation_type) and type(argument) is str

    def _validate_path(self, path: Path):
        validation_type = self._validation_type[self._last_validated_index]
        if validation_type == PathType.Directory and not path.is_dir():
            raise Exception(f'The path [{path}] either does not exist or does not point to a directory.')
        elif validation_type == PathType.File and not path.is_file():
            raise Exception(f'The path [{path}] either does not exist or does not point to a file.')
        self._last_validated_index = self._last_validated_index + 1


def valid_path(*validation_types: PathType):
    """
    Provides a layer of parsing and validation on the decorated function to allow for automated conversion of a string
    parameter into a valid Path object of the specified type.

    :param validation_types: A variable sized tuple specifying how many string arguments passed to the decorated
    function will be converted to a Path object and validated. Validation will check whether the Path is either
    a file or folder depending on the specified type.
    """
    def inner(function):
        def wrapper(*arguments):
            validator = _ArgumentValidator(validation_types)
            processed_arguments = list(map(validator.augment_argument, arguments))
            return function(*processed_arguments)
        return wrapper
    return inner
