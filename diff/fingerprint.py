from pathlib import Path

import click

import diff.checksum as check
from diff.util import valid_path, FILE, log_exception


@log_exception
@valid_path(FILE)
def _fingerprint(file_path: Path):
    checksum_string = check.calculate_checksum(file_path)

    print('\n===== ===== ===== ===== =====\n')
    print(f'Checksum of file is:\n\t{checksum_string}')
    print('\n===== ===== ===== ===== =====\n')


@click.command('checksum')
@click.argument('file')
def fingerprint(file: str):
    _fingerprint(file)
