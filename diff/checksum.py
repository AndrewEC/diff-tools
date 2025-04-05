import click

from diff.core.tree import AVAILABLE_HASH_ALGORITHMS, DEFAULT_HASH_ALGORITHM
from diff.core.cli import CliChecksum


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
    return CliChecksum().calculate(path, algo)


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
    return CliChecksum().verify(path, hash, algo)


@click.group()
def checksum():
    pass


checksum.add_command(_calculate)
checksum.add_command(_verify)
