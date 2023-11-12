from pathlib import Path

import click

from diff.tree import compute_file_hash


@click.command('calculate')
@click.argument('path')
@click.option('--algo', '-a', type=click.Choice(['sha256', 'sha512']), default='sha256', help='The preferred algorithm to hash the file with.')
def _calculate(path: str, algo: str):
    """
    Computes the hash of a given file.

    path: The path to the file to compute the hash of. This must be an existing file and not a directory.
    """
    path_to_compute = Path(path)
    if not path_to_compute.is_file():
        raise ValueError('The path to compute the checksum of must point to a file. The path provided either does not exist or is not a file.')
    file_hash = compute_file_hash(path_to_compute, algo)
    print(f'The file hash is: {file_hash}')


@click.command('validate')
@click.argument('path')
@click.argument('hash')
@click.option('--algo', '-a', type=click.Choice(['sha256', 'sha512']), default='sha256', help='The preferred algorithm to hash the file with.')
def _validate(path: str, hash: str, algo: str):
    """
    Computes the has of a given file and compares the computed hash to the provided hash for equality.

    path: The path to the file to compute the hash of. This must be an existing file and not a directory.

    hash: The hash previously computed to compare against.
    """
    path_to_compute = Path(path)
    if not path_to_compute.is_file():
        raise ValueError('The path to compute the checksum of must point to a file. The path provided either does not exist or is not a file.')
    file_hash = compute_file_hash(path_to_compute, algo)
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
checksum.add_command(_validate)
