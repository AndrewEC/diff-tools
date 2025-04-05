import click

from diff.core.cli import CliBetween
from diff.core.tree import AVAILABLE_HASH_ALGORITHMS, DEFAULT_HASH_ALGORITHM


@click.command()
@click.argument('first')
@click.argument('second')
@click.option(
    '--checksum',
    '-c',
    is_flag=True,
    help='Specifies if the checksum should be calculated for each file found in the scan.'
)
@click.option(
    '--algo',
    '-a',
    type=click.Choice(AVAILABLE_HASH_ALGORITHMS),
    default=DEFAULT_HASH_ALGORITHM,
    help='The preferred algorithm to hash the file with.'
)
def between(first: str, second: str, checksum: bool, algo: str):
    """
    Scans two directories, specified by the first and second paths, and compares the structure of the two.

    This will identify all files that are similar (have the same name but different size or checksum), all files
    that exist within the first directory but not the second, and all files that exist within the second directory but
    not the first.
    """
    CliBetween().between(first, second, checksum, algo)
