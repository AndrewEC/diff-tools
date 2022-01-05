from typing import List, Tuple
import math
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


_TASK_COUNT = 3
_LARGE_FILE_SIZE_THRESHOLD = 200
_LARGE_FILE_CHUNK_SIZE = 250 * 1024 * 1024


class TaskArguments:

    def __init__(self, path: Path, chunk_info: Tuple[int, int], max_block_size: int):
        self.path = path
        self.start, self.size = chunk_info
        self.max_block_size = max_block_size


def _calculate_max_block_size() -> int:
    return hashlib.sha256().block_size * 128


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
    if remaining > max_block_size:
        return max_block_size
    return remaining


def _calculate_checksum_for_chunk(task_arguments: TaskArguments) -> str:
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


def _large_file_pseudo_checksum(path: Path) -> str:
    block_info = _calculate_block_info(path)
    max_block_size = _calculate_max_block_size()
    task_arguments = [TaskArguments(path, block_info, max_block_size) for block_info in block_info]
    with ThreadPoolExecutor(_TASK_COUNT) as executor:
        combined_hash = ''.join(list(executor.map(_calculate_checksum_for_chunk, task_arguments)))
    return hashlib.shake_256(bytes(combined_hash, 'utf-8')).hexdigest(30)


def _small_file_checksum(path: Path) -> str:
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


def calculate_checksum(path: Path) -> str:
    print(f'Calculating checksum of file: [{path}]')
    if _file_size_in_megabytes(path) >= _LARGE_FILE_SIZE_THRESHOLD:
        print(f'File [{path}] is over 200 megabytes. Checksum will be calculated as a pseudo checksum.')
        return _large_file_pseudo_checksum(path)
    return _small_file_checksum(path)
