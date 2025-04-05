from typing import Callable
from pathlib import Path

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
        file_hash = self._compute_file_hash(path, algo)
        if file_hash != hash:
            self._print_function('The calculated file has and the existing hash do not match.')
            self._print_function('Hashes are:')
            self._print_function(f'\tExisting: {hash}')
            self._print_function(f'\tComputed: {file_hash}')
        else:
            self._print_function('The calculated file hash and the existing provided hash match.')

    def _compute_file_hash(self, path: str, algo: str) -> str:
        path_to_compute = Path(path)
        if not path_to_compute.is_file():
            raise NotAFileException('file', path_to_compute)
        return self._checksum.compute_file_checksum(path_to_compute, algo)
