from pathlib import Path
import unittest
from unittest.mock import Mock, patch, call, ANY

from diff.core.cli import CliBetween
from diff.core.tree import TreeLoader
from diff.core.tree.diff import TreeDiff, SimilarityPrinter

from diff.tests.util import fully_qualified_name


class CliBetweenTests(unittest.TestCase):

    @patch(fully_qualified_name(SimilarityPrinter))
    @patch(fully_qualified_name(TreeLoader))
    @patch(fully_qualified_name(TreeDiff))
    def test_between(self,
                     mock_tree_diff: TreeDiff,
                     mock_tree_loader: TreeLoader,
                     mock_similarity_printer: SimilarityPrinter):

        checksum_algo = 'sha256'

        first_path = Path(__file__).absolute().parent.parent.joinpath('tree')
        second_path = Path(__file__).absolute().parent.parent.joinpath('util')

        first_tree = Mock()
        second_tree = Mock()

        def mock_return(path: Path, checksum: bool, algo: str):
            if path == first_path:
                return first_tree
            elif path == second_path:
                return second_tree
            raise Exception(f'Unknown path parameter: [{path}].')

        mock_tree_loader.read_tree_from_disk = Mock(side_effect=mock_return)

        mock_similarity_printer.print_similarity_results = Mock()

        diff_result = Mock()
        mock_tree_diff.diff_between_trees = Mock(return_value=diff_result)

        (CliBetween(mock_tree_diff, mock_tree_loader, mock_similarity_printer)
         .between(str(first_path), str(second_path), True, checksum_algo))

        mock_tree_loader.read_tree_from_disk.assert_has_calls([
            call(first_path, True, checksum_algo),
            call(second_path, True, checksum_algo)
        ], True)

        mock_tree_diff.diff_between_trees.assert_called_once_with(first_tree, second_tree)
        mock_similarity_printer.print_similarity_results.assert_called_once_with(diff_result, ANY)
