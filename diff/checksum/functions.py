from typing import List, Tuple, Callable, Any
import enum
import math
import hashlib
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor


_TASK_COUNT = 3
_LARGE_FILE_SIZE_THRESHOLD = 200
_LARGE_FILE_CHUNK_SIZE = 200 * 1024 * 1024


class _TaskArguments:

    def __init__(self, path: Path, chunk_info: Tuple[int, int], max_block_size: int):
        self.path = path
        self.start, self.size = chunk_info
        self.max_block_size = max_block_size


class ChecksumFunctionType(enum.Enum):
    Exact = 0
    Pseudo = 1


class ChecksumFunction:

    def __init__(self, function_type: ChecksumFunctionType, function: Callable[[Path], str]):
        self.function_type = function_type
        self.apply = function


def _get_hashing_function() -> Any:
    return hashlib.sha256()


def _calculate_max_block_size() -> int:
    return _get_hashing_function().block_size * 128


def _calculate_block_info(path: Path) -> List[Tuple[int, int]]:
    file_size = path.stat().st_size
    last_chunk_size = file_size % _LARGE_FILE_CHUNK_SIZE

    if last_chunk_size == 0:
        full_chunk_count = math.ceil(file_size / _LARGE_FILE_CHUNK_SIZE)
        return [(i * _LARGE_FILE_CHUNK_SIZE, _LARGE_FILE_CHUNK_SIZE) for i in range(full_chunk_count)]

    # The number of chunks that will have a byte count equal to _LARGE_FILE_CHUNK_SIZE
    full_chunk_count = math.ceil(file_size / _LARGE_FILE_CHUNK_SIZE) - 1
    chunks = [(i * _LARGE_FILE_CHUNK_SIZE, _LARGE_FILE_CHUNK_SIZE) for i in range(full_chunk_count)]

    # The last chunk that will have a byte count less than the _LARGE_FILE_CHUNK_SIZE
    chunks.append((_LARGE_FILE_CHUNK_SIZE * full_chunk_count, last_chunk_size))
    return chunks


def _next_block_size(remaining: int, max_block_size: int) -> int:
    return min(remaining, max_block_size)


def _calculate_checksum_for_chunk(task_arguments: _TaskArguments) -> str:
    """
    Takes in an argument identifying the location of the file, the starting byte of the chunk, and the number of bytes
    that make up the chunk, and returns a hash of the chunk.

    :param task_arguments: Specifies the file path, chunk start, and size.
    :return: A hash of the chunk, portion, of the input file.
    """
    remaining = task_arguments.size
    hasher = _get_hashing_function()
    with open(task_arguments.path, 'rb') as file:
        file.seek(task_arguments.start, 0)
        read = file.read(_next_block_size(remaining, task_arguments.max_block_size))
        while len(read) > 0:
            hasher.update(read)
            remaining = remaining - len(read)
            read = file.read(_next_block_size(remaining, task_arguments.max_block_size))
    return hasher.hexdigest()


def _pseudo_checksum(path: Path) -> str:
    block_info = _calculate_block_info(path)
    max_block_size = _calculate_max_block_size()
    task_arguments = [_TaskArguments(path, block, max_block_size) for block in block_info]
    with ThreadPoolExecutor(_TASK_COUNT) as executor:
        combined_hash = ''.join(list(executor.map(_calculate_checksum_for_chunk, task_arguments)))
    return _get_hashing_function().update(bytes(combined_hash, 'utf-8')).hexdigest()


def _exact_checksum(path: Path) -> str:
    hasher = _get_hashing_function()
    block_size = 128 * hasher.block_size
    with open(path, 'rb') as file:
        read = file.read(block_size)
        while len(read) > 0:
            hasher.update(read)
            read = file.read(block_size)
    return hasher.hexdigest()


def _file_size_in_megabytes(path: Path) -> float:
    return path.stat().st_size / 1024 / 1024


def get_checksum_function(path: Path, force_exact: bool = False) -> ChecksumFunction:
    """
    Gets the appropriate function for computing the checksum of a given file.

    If the file size is below the threshold of 200 megabytes then an exact Sha 256 hash will be used.

    If the file size is above the threshold then this will return a pseudo hash function that will split the file up
    into 200 megabyte chunks, calculate the size of each chunk, the combine the resulting hashes into a single hash.
    The pseudo function is multithreaded and will use a thread pool executor with a maximum of 3 threads.

    :param path: The path to the file to calculate the checksum of.
    :param force_exact: If true this will force the use of the exact hashing function even if the file size is above
    the 200 megabyte threshold.
    :return: A function that can be applied to calculate the hash of a given set of files. The function instance
    can be re-used.
    """
    if not force_exact and _file_size_in_megabytes(path) >= _LARGE_FILE_SIZE_THRESHOLD:
        return ChecksumFunction(ChecksumFunctionType.Pseudo, _pseudo_checksum)
    return ChecksumFunction(ChecksumFunctionType.Exact, _exact_checksum)
