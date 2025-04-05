import click

from diff.core.cli import CliScan
from diff.core.tree import AVAILABLE_HASH_ALGORITHMS, DEFAULT_HASH_ALGORITHM


@click.command('folder')
@click.argument('path')
@click.argument('output')
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
def _folder(path: str, output: str, checksum: bool, algo: str):
    """
    Scans a given directory and saves the results of the scan to a yaml file.

    path: The path to the directory to be scanned.

    output: The path where the yaml file containing the results of the scan should be saved to.
    """
    CliScan().folder(path, output, checksum, algo)


@click.command('verify')
@click.argument('scan')
@click.option(
    '--checksum',
    '-c',
    is_flag=True,
    help='Specifies if the checksum should be calculated for each file found in the scan.'
)
def _verify(scan: str, checksum: bool):
    """
    Checks if the results of a previous scan match what is currently on disk.

    This will check to see if any files have been deleted, added, or have changed either in terms of their size or
    their checksum.

    scan: The path to the yaml file containing the results of a previous scan.
    """
    CliScan().verify(scan, checksum)


@click.group()
def scan():
    pass


scan.add_command(_verify)
scan.add_command(_folder)
