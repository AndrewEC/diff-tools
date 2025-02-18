from pathlib import Path
import click

import diff.tree as trees
from diff.errors import NotADirectoryException, NotAFileException


class Decorator(trees.DiffMessageDecorator):

    def first_tree_has_diff_message(self) -> str:
        return 'The following files were found on disk but not in the previous scan result (new files):'

    def first_tree_no_diff_message(self) -> str:
        return 'All files found on disk are also listed in the previous scan result.'

    def second_tree_has_diff_message(self) -> str:
        return 'The following files were listed in the previous scan result but not on disk (deleted files):'

    def second_tree_no_diff_message(self) -> str:
        return 'All files listed in the previous scan result were found on disk.'


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
    type=click.Choice(trees.AVAILABLE_HASH_ALGORITHMS),
    default=trees.DEFAULT_HASH_ALGORITHM,
    help='The preferred algorithm to hash the file with.'
)
def _folder(path: str, output: str, checksum: bool, algo: str):
    """
    Scans a given directory and saves the results of the scan to a yaml file.

    path: The path to the directory to be scanned.

    output: The path where the yaml file containing the results of the scan should be saved to.
    """

    path_to_scan = Path(path).absolute()
    if not path_to_scan.is_dir():
        raise NotADirectoryException('path to scan', path_to_scan)

    output_path = Path(output).absolute()
    if output_path.is_file():
        raise ValueError(f'The output path already exists. Delete the following file and try again: [{output_path}]')

    root_node = trees.read_tree_from_disk(path_to_scan, checksum, algo)

    trees.to_yaml_file(output_path, root_node)
    print(f'Scan results saved to: [{output_path}]')


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

    scan_path = Path(scan).absolute()
    if not scan_path.is_file():
        raise NotAFileException('previous scan', scan_path)

    scan_tree = trees.read_tree_from_yaml(scan_path)
    root_path = scan_tree.path_to_node()
    if not root_path.is_dir():
        raise Exception(f'Could not verify scan because the original scanned directory could not be found at: [{root_path}]')

    disk_tree = trees.read_tree_from_disk(root_path, checksum, scan_tree.checksum_algo)

    diff_result = trees.diff_between_trees(scan_tree, disk_tree)
    trees.print_similarity_results(diff_result, Decorator())


@click.group()
def scan():
    pass


scan.add_command(_verify)
scan.add_command(_folder)
