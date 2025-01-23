from pathlib import Path

import click

from diff.tree import compute_file_checksum, AVAILABLE_HASH_ALGORITHMS, DEFAULT_HASH_ALGORITHM
from diff.errors import NotAFileException


def _compute_file_hash(path: str, algo: str) -> str:
    path_to_compute = Path(path)
    if not path_to_compute.is_file():
        raise NotAFileException('file', path_to_compute)
    return compute_file_checksum(path_to_compute, algo)


@click.command('calculate')
@click.argument('path')
@click.option(
    '--algo',
    '-a',
    type=click.Choice(AVAILABLE_HASH_ALGORITHMS),
    default=DEFAULT_HASH_ALGORITHM,
    help='The preferred algorithm to hash the file with.'
)
def _calculate(path: str, algo: str):
    """
    Computes the hash of a given file.

    path: The path to the file to compute the hash of. This must be an existing file and not a directory.
    """
    file_hash = _compute_file_hash(path, algo)
    print(f'The {algo} file hash is: {file_hash}')


@click.command('verify')
@click.argument('path')
@click.argument('hash')
@click.option(
    '--algo',
    '-a',
    type=click.Choice(AVAILABLE_HASH_ALGORITHMS),
    default=DEFAULT_HASH_ALGORITHM,
    help='The preferred algorithm to hash the file with.'
)
def _verify(path: str, hash: str, algo: str):
    """
    Computes the hash of a given file and compares said computed hash to the provided hash for equality.

    path: The path to the file to compute the hash of. This must be an existing file and not a directory.

    hash: The hash previously computed to compare against.
    """
    file_hash = _compute_file_hash(path, algo)
    if file_hash != hash:
        print('The calculated file has and the existing hash do not match.')
        print('Hashes are:')
        print(f'\tExisting: {hash}')
        print(f'\tComputed: {file_hash}')
    else:
        print('The calculated file hash and the existing provided hash match.')


@click.group()
def checksum():
    pass


checksum.add_command(_calculate)
checksum.add_command(_verify)
