from typing import Any
import hashlib
from pathlib import Path

from diff.errors import UnsupportedAlgorithmException


def _try_get_hash_function(algo: str) -> Any:
    if not hasattr(hashlib, algo):
        return None
    return getattr(hashlib, algo)


def compute_file_checksum(path: Path, algo: str) -> str:
    """
    Computes the hash of a file at the given path using the specified hash algorithm.

    :param path: The absolute path to the file on disk whose hash is to be computed.
    :param algo: The algorithm to use to compute the hash of the file.
    :return: The computed hash of the file.
    :raises UnsupportedAlgorithmException: Raised if the specified hashing algorithm does not
        exist with the hashlib module.
    """
    print(f'Computing checksum of file: [{path}]')
    hash_function = _try_get_hash_function(algo)
    if not callable(hash_function):
        raise UnsupportedAlgorithmException(algo)

    file_hash = getattr(hashlib, algo)()
    with open(path, 'rb') as file:
        while chunk := file.read(file_hash.block_size):
            file_hash.update(chunk)
    return file_hash.hexdigest()
