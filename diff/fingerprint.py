from pathlib import Path

import click

from diff.checksum import calculate_checksum
from diff.util.decorators import valid_path, PathType, log_exception


@log_exception
@valid_path(PathType.File)
def _fingerprint(file_path: Path):
    checksum_string = calculate_checksum(file_path)

    print('\n===== ===== ===== ===== =====\n')
    print(f'Checksum of file is:\n\t{checksum_string}')
    print('\n===== ===== ===== ===== =====\n')


@click.command('checksum')
@click.argument('file')
def fingerprint(file: str):
    _fingerprint(file)
