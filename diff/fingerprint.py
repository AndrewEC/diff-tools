from pathlib import Path

import click

from diff.checksum import get_checksum_function, ChecksumFunctionType
from diff.util.decorators import valid_path, PathType, log_exception


@log_exception('Could not fingerprint the input file.')
@valid_path(PathType.File)
def _fingerprint(file_path: Path, exact_hash: bool):
    print(f'Calculating checksum of file: [{file_path}]')
    checksum_function = get_checksum_function(file_path, exact_hash)
    if checksum_function.function_type == ChecksumFunctionType.Pseudo:
        print(f'File [{file_path}] is over 200 megabytes. Checksum will be calculated as a pseudo checksum.')
    checksum_string = checksum_function.apply(file_path)

    print('\n===== ===== ===== ===== =====\n')
    print(f'Checksum of file is:\n\t{checksum_string}')
    print('\n===== ===== ===== ===== =====\n')


@click.command('checksum')
@click.argument('file')
@click.option('--exact-hash', '-e', is_flag=True)
def fingerprint_command(file: str, exact_hash: bool):
    _fingerprint(file, exact_hash)
