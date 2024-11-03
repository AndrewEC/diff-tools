from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import click

import diff.tree as trees
from diff.errors import NotADirectoryException


class Decorator(trees.DiffMessageDecorator):

    def __init__(self, first_tree: trees.Node, second_tree: trees.Node):
        self._first = first_tree
        self._second = second_tree

    def first_tree_has_diff_message(self) -> str:
        return (f'The following files were found in [{self._second.path_to_node()}] '
                f'but not in [{self._first.path_to_node()}]:')

    def first_tree_no_diff_message(self) -> str:
        return f'All files found in [{self._second.path_to_node()}] were also found in [{self._first.path_to_node()}].'

    def second_tree_has_diff_message(self) -> str:
        return f'The following files were found in [{self._first.path_to_node()}] but not in [{self._second.path_to_node()}]:'

    def second_tree_no_diff_message(self) -> str:
        return f'All files found in [{self._first.path_to_node()}] were also found in [{self._second.path_to_node()}].'


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
    type=click.Choice(trees.AVAILABLE_HASH_ALGORITHMS),
    default=trees.DEFAULT_HASH_ALGORITHM,
    help='The preferred algorithm to hash the file with.'
)
def between(first: str, second: str, checksum: bool, algo: str):
    """
    Scans two directories, specified by the first and second paths, and compares the structure of the two.

    This will identify all files that are similar (have the same name but different size or checksum), all files
    that exist within the first directory but not the second, and all files that exist within the second directory but
    not the first.
    """

    first_path = Path(first).absolute()
    if not first_path.is_dir():
        raise NotADirectoryException('first path', first_path)

    second_path = Path(second).absolute()
    if not second_path.is_dir():
        raise NotADirectoryException('second path', second_path)

    if first == second:
        raise ValueError('The first path to scan and the second path to scan cannot refer to the same location.')

    with ThreadPoolExecutor(max_workers=2) as executor:
        first_execution = executor.submit(trees.read_tree_from_disk, first_path, checksum, algo)
        second_execution = executor.submit(trees.read_tree_from_disk, second_path, checksum, algo)
        first_tree = first_execution.result()
        second_tree = second_execution.result()

    diff_result = trees.diff_between_trees(first_tree, second_tree)
    trees.print_similarity_results(diff_result, Decorator(first_tree, second_tree))
