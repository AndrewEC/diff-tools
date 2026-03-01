from typing import Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from diff.core.errors import NotAFileException
from diff.core.util import Checksum, CHECKSUM_SINGLETON


class CliChecksum:

    def __init__(self,
                 checksum: Checksum = CHECKSUM_SINGLETON,
                 print_function: Callable[[str], None] = print):
        self._checksum = checksum
        self._print_function = print_function

    def calculate(self, path: str, algo: str):
        file_hash = self._compute_file_hash(path, algo)
        self._print_function(f'The {algo} file hash is: {file_hash}')

    def verify(self, path: str, hash: str, algo: str):
        hash = hash.upper()
        file_hash = self._compute_file_hash(path, algo)
        if file_hash != hash:
            self._print_function('The calculated file has and the existing hash do not match.')
            self._print_function('Hashes are:')
            self._print_function(f'\tExisting: {hash}')
            self._print_function(f'\tComputed: {file_hash}')
        else:
            self._print_function('The calculated file hash and the existing provided hash match.')
    
    def compare(self, first: str, second: str, algo: str):
        first_path = Path(first)
        if not first_path.is_file():
            raise NotAFileException('first', first_path)
        
        second_path = Path(second)
        if not second_path.is_file():
            raise NotAFileException('second', second_path)
        
        if first_path == second_path:
            raise ValueError('The first file path and the second file path cannot refer to the same file. Specify different files and try again.')

        with ThreadPoolExecutor(max_workers=2) as executor:
            first_execution = executor.submit(self._checksum.compute_file_checksum, first_path, algo)
            second_execution = executor.submit(self._checksum.compute_file_checksum, second_path, algo)
            first_result = first_execution.result()
            second_result = second_execution.result()

        if first_result == second_result:
            self._print_function(f'Both files have the same {algo} hash.')
            self._print_function(f'The hash of both files is: {first_result}')
        else:
            self._print_function(f'The files have different {algo} hashes.')
            self._print_function(f'\t{first} -> {first_result}')
            self._print_function(f'\t{second} -> {second_result}')

    def _compute_file_hash(self, path: str, algo: str) -> str:
        path_to_compute = Path(path)
        if not path_to_compute.is_file():
            raise NotAFileException('file', path_to_compute)
        return self._checksum.compute_file_checksum(path_to_compute, algo)
