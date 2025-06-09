from pathlib import Path
import unittest
from unittest.mock import Mock, patch, ANY

from diff.core.cli import CliScan
from diff.core.tree import TreeLoader, YamlSerialization
from diff.core.tree.diff import TreeDiff, SimilarityPrinter

from diff.tests.util import fully_qualified_name


class CliScanTests(unittest.TestCase):

    @patch(fully_qualified_name(YamlSerialization))
    @patch(fully_qualified_name(TreeDiff))
    @patch(fully_qualified_name(TreeLoader))
    def test_folder(self,
                    mock_tree_loader: TreeLoader,
                    mock_tree_diff: TreeDiff,
                    mock_yaml_serialization: YamlSerialization):

        mock_print_function = Mock()

        checksum_algo = 'sha256'
        mock_root_node = Mock()
        mock_tree_loader.read_tree_from_disk = Mock(return_value=mock_root_node)

        mock_yaml_serialization.to_yaml_file = Mock()

        input_path = Path(__file__).absolute().parent
        output_path = input_path.joinpath('scan.yml')

        (CliScan(mock_tree_loader, mock_tree_diff, mock_yaml_serialization, Mock(), mock_print_function)
         .folder(str(input_path), str(output_path), True, checksum_algo))

        mock_tree_loader.read_tree_from_disk.assert_called_once_with(input_path, True, checksum_algo)
        mock_yaml_serialization.to_yaml_file.assert_called_once_with(output_path, mock_root_node)
        mock_print_function.assert_called_once_with(f'Scan results saved to: [{output_path}]')

    @patch(fully_qualified_name(SimilarityPrinter))
    @patch(fully_qualified_name(YamlSerialization))
    @patch(fully_qualified_name(TreeDiff))
    @patch(fully_qualified_name(TreeLoader))
    def test_verify(self,
                    mock_tree_loader: TreeLoader,
                    mock_tree_diff: TreeDiff,
                    mock_yaml_serialization: YamlSerialization,
                    mock_similarity_printer: SimilarityPrinter):

        checksum_algo = 'sha256'
        scan_file_path = Path(__file__).absolute()

        original_scan_folder = Path(__file__).absolute().parent
        mock_node = Mock(
            path_to_node=Mock(return_value=original_scan_folder),
            checksum_algo=checksum_algo
        )

        mock_print_function = Mock()
        mock_tree_loader.read_tree_from_yaml = Mock(return_value=mock_node)

        disk_tree = Mock()
        mock_tree_loader.read_tree_from_disk = Mock(return_value=disk_tree)

        diff_result = Mock()
        mock_tree_diff.diff_between_trees = Mock(return_value=diff_result)

        mock_similarity_printer.print_similarity_results = Mock()

        (CliScan(mock_tree_loader, mock_tree_diff, mock_yaml_serialization, mock_similarity_printer, mock_print_function)
         .verify(str(scan_file_path), True))

        mock_tree_loader.read_tree_from_yaml.assert_called_once_with(scan_file_path)
        mock_tree_loader.read_tree_from_disk.assert_called_once_with(original_scan_folder, True, checksum_algo)
        mock_similarity_printer.print_similarity_results.assert_called_once_with(diff_result, ANY)

        mock_node.path_to_node.assert_called_once()
