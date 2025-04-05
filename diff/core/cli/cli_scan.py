from typing import Callable
from pathlib import Path

from diff.core.tree import (
    TreeLoader,
    TREE_LOADER_SINGLETON,
    YamlSerialization,
    YAML_SERIALIZATION_SINGLETON
)
from diff.core.tree.diff import (
    DiffMessageDecorator,
    TreeDiff,
    TREE_DIFF_SINGLETON,
    SimilarityPrinter,
    SIMILARITY_PRINTER_SINGLETON
)
from diff.core.errors import NotADirectoryException, NotAFileException


class CliScan:

    def __init__(self,
                 tree_loader: TreeLoader = TREE_LOADER_SINGLETON,
                 tree_diff: TreeDiff = TREE_DIFF_SINGLETON,
                 yaml_serialization: YamlSerialization = YAML_SERIALIZATION_SINGLETON,
                 similarity_printer: SimilarityPrinter = SIMILARITY_PRINTER_SINGLETON,
                 print_function: Callable[[str], None] = print):

        self._tree_loader = tree_loader
        self._tree_diff = tree_diff
        self._yaml_serialization = yaml_serialization
        self._similarity_printer = similarity_printer
        self._print_function = print_function

    def folder(self, path: str, output: str, checksum: bool, algo: str):
        path_to_scan = Path(path).absolute()
        if not path_to_scan.is_dir():
            raise NotADirectoryException('path to scan', path_to_scan)

        output_path = Path(output).absolute()
        if output_path.is_file():
            raise ValueError(f'The output path already exists. Delete the following file and try again: [{output_path}]')

        root_node = self._tree_loader.read_tree_from_disk(path_to_scan, checksum, algo)

        self._yaml_serialization.to_yaml_file(output_path, root_node)
        self._print_function(f'Scan results saved to: [{output_path}]')

    def verify(self, scan: str, checksum: bool):
        scan_path = Path(scan).absolute()
        if not scan_path.is_file():
            raise NotAFileException('previous scan', scan_path)

        scan_tree = self._tree_loader.read_tree_from_yaml(scan_path)
        root_path = scan_tree.path_to_node()
        if not root_path.is_dir():
            raise Exception(f'Could not verify scan because the original scanned directory could not be found at: [{root_path}]')

        disk_tree = self._tree_loader.read_tree_from_disk(root_path, checksum, scan_tree.checksum_algo)

        diff_result = self._tree_diff.diff_between_trees(scan_tree, disk_tree)
        self._similarity_printer.print_similarity_results(diff_result, _Decorator())


class _Decorator(DiffMessageDecorator):

    def first_tree_has_diff_message(self) -> str:
        return 'The following files were found on disk but not in the previous scan result (new files):'

    def first_tree_no_diff_message(self) -> str:
        return 'All files found on disk are also listed in the previous scan result.'

    def second_tree_has_diff_message(self) -> str:
        return 'The following files were listed in the previous scan result but not on disk (deleted files):'

    def second_tree_no_diff_message(self) -> str:
        return 'All files listed in the previous scan result were found on disk.'
