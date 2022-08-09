from typing import List, Tuple, Callable
import enum
import math
import hashlib
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor


_TASK_COUNT = 3
_LARGE_FILE_SIZE_THRESHOLD = 200
_LARGE_FILE_CHUNK_SIZE = 250 * 1024 * 1024


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


def _calculate_max_block_size() -> int:
    return hashlib.shake_256().block_size * 128


def _calculate_block_info(path: Path) -> List[Tuple[int, int]]:
    size = path.stat().st_size
    last_chunk_size = size % _LARGE_FILE_CHUNK_SIZE

    if last_chunk_size == 0:
        full_chunk_count = math.ceil(size / _LARGE_FILE_CHUNK_SIZE)
        return [(i * _LARGE_FILE_CHUNK_SIZE, _LARGE_FILE_CHUNK_SIZE) for i in range(full_chunk_count)]

    full_chunk_count = math.ceil(size / _LARGE_FILE_CHUNK_SIZE) - 1
    chunks = [(i * _LARGE_FILE_CHUNK_SIZE, _LARGE_FILE_CHUNK_SIZE) for i in range(full_chunk_count)]
    chunks.append((_LARGE_FILE_CHUNK_SIZE * full_chunk_count, last_chunk_size))
    return chunks


def _next_block_size(remaining: int, max_block_size: int) -> int:
    return min(remaining, max_block_size)


def _calculate_checksum_for_chunk(task_arguments: _TaskArguments) -> str:
    remaining = task_arguments.size
    hasher = hashlib.shake_256()
    with open(task_arguments.path, 'rb') as file:
        file.seek(task_arguments.start, 0)
        read = file.read(_next_block_size(remaining, task_arguments.max_block_size))
        while len(read) > 0:
            hasher.update(read)
            remaining = remaining - len(read)
            read = file.read(_next_block_size(remaining, task_arguments.max_block_size))
    return hasher.hexdigest(30)


def _pseudo_checksum(path: Path) -> str:
    block_info = _calculate_block_info(path)
    max_block_size = _calculate_max_block_size()
    task_arguments = [_TaskArguments(path, block_info, max_block_size) for block_info in block_info]
    with ThreadPoolExecutor(_TASK_COUNT) as executor:
        combined_hash = ''.join(list(executor.map(_calculate_checksum_for_chunk, task_arguments)))
    return hashlib.shake_256(bytes(combined_hash, 'utf-8')).hexdigest(30)


def _exact_checksum(path: Path) -> str:
    hasher = hashlib.shake_256()
    block_size = 128 * hasher.block_size
    with open(path, 'rb') as file:
        read = file.read(block_size)
        while len(read) > 0:
            hasher.update(read)
            read = file.read(block_size)
    return hasher.hexdigest(30)


def _file_size_in_megabytes(path: Path) -> float:
    return path.stat().st_size / 1024 / 1024


def get_checksum_function(path: Path, force_exact: bool = False) -> ChecksumFunction:
    if not force_exact and _file_size_in_megabytes(path) >= _LARGE_FILE_SIZE_THRESHOLD:
        return ChecksumFunction(ChecksumFunctionType.Pseudo, _pseudo_checksum)
    return ChecksumFunction(ChecksumFunctionType.Exact, _exact_checksum)
