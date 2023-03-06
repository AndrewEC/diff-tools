from pathlib import Path

import click

from diff.checksum import get_checksum_function, ChecksumFunctionType
from diff.util.decorators import valid_path, PathType, log_exception


def _calculate_hash(file_path: Path, exact_hash: bool) -> str:
    checksum_function = get_checksum_function(file_path, exact_hash)
    if checksum_function.function_type == ChecksumFunctionType.Pseudo:
        print(f'File [{file_path}] is over 200 megabytes. Checksum will be calculated as a pseudo checksum.')
    return checksum_function.apply(file_path)


@log_exception('Could not generate hash of the input file.')
@valid_path(PathType.File)
def _hash(file_path: Path, exact_hash: bool):
    print(f'Calculating SHA256 checksum of file: [{file_path}]')
    file_checksum = _calculate_hash(file_path, exact_hash)

    print('\n===== ===== ===== ===== =====\n')
    print(f'Sha256 checksum of file is:\n\t{file_checksum}')
    print('\n===== ===== ===== ===== =====\n')


@log_exception('Could not validate the hash of the input file.')
@valid_path(PathType.File)
def _do_hashes_match(file_path: Path, hash: str):
    actual_hash = _calculate_hash(file_path, True)

    print('\n===== ===== ===== ===== =====\n')
    print(f'Sha256 checksum of file is:\n\t{actual_hash}')
    if actual_hash == hash:
        print(f'The file hash matches the input hash.')
    else:
        print(f'The actual file hash does not match the input file hash. Ensure the input hash is generated using SHA 256.')
        print(f'Hashes:\n\t{actual_hash}\n\t{hash}')
    print('\n===== ===== ===== ===== =====\n')


@click.command('calculate')
@click.argument('file')
@click.option('--exact-hash', '-e', is_flag=True)
def _generate_hash_command(file: str, exact_hash: bool):
    """
    Calculates the SHA-256 hash of the given file.
    """
    _hash(file, exact_hash)


@click.command('verify')
@click.argument('file')
@click.argument('hash')
def _validate_hash_command(file: str, hash: str):
    """
    Calculates the SHA-256 hash of the given file and verifies if it matches the input hash.
    """
    _do_hashes_match(file, hash)


@click.group('hash')
def hash_group():
    pass


hash_group.add_command(_generate_hash_command)
hash_group.add_command(_validate_hash_command)
