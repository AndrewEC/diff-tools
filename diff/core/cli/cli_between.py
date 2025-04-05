from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from diff.core.tree.diff import (
    TreeDiff,
    TREE_DIFF_SINGLETON,
    SimilarityPrinter,
    SIMILARITY_PRINTER_SINGLETON,
    DiffMessageDecorator
)
from diff.core.tree import (
    TreeLoader,
    TREE_LOADER_SINGLETON,
    Node
)
from diff.core.errors import NotADirectoryException


class CliBetween:

    def __init__(self,
                 tree_diff: TreeDiff = TREE_DIFF_SINGLETON,
                 tree_loader: TreeLoader = TREE_LOADER_SINGLETON,
                 similarity_printer: SimilarityPrinter = SIMILARITY_PRINTER_SINGLETON):
        self._tree_diff = tree_diff
        self._tree_loader = tree_loader
        self._similarity_printer = similarity_printer

    def between(self, first: str, second: str, checksum: bool, algo: str):
        first_path = Path(first).absolute()
        if not first_path.is_dir():
            raise NotADirectoryException('first path', first_path)

        second_path = Path(second).absolute()
        if not second_path.is_dir():
            raise NotADirectoryException('second path', second_path)

        if first == second:
            raise ValueError('The first path to scan and the second path to scan cannot refer to the same location.')

        with ThreadPoolExecutor(max_workers=2) as executor:
            first_execution = executor.submit(self._tree_loader.read_tree_from_disk, first_path, checksum, algo)
            second_execution = executor.submit(self._tree_loader.read_tree_from_disk, second_path, checksum, algo)
            first_tree = first_execution.result()
            second_tree = second_execution.result()

        diff_result = self._tree_diff.diff_between_trees(first_tree, second_tree)
        self._similarity_printer.print_similarity_results(diff_result, _Decorator(first_tree, second_tree))


class _Decorator(DiffMessageDecorator):

    def __init__(self, first_tree: Node, second_tree: Node):
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
