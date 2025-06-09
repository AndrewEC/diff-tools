from typing import Dict, Any
from pathlib import Path

import unittest
from unittest.mock import patch, Mock

from diff.core.errors import InvalidScanFileException
from diff.core.tree import TreeLoader, YamlSerialization
from diff.core.util import Checksum, either

from diff.tests.util import fully_qualified_name


class TreeLoaderTests(unittest.TestCase):

    @patch(fully_qualified_name(YamlSerialization))
    def test_read_tree_from_yaml(self, mock_yaml: YamlSerialization):
        values: Dict[str, Any] = {
            'name': 'test_name',
            'checksum': 'test_checksum',
            'checksum_algo': 'test_checksum_algo',
            'size': 88
        }
        mock_yaml.read_yaml_file = Mock(return_value=values)

        file_path = Path(__file__)

        actual = TreeLoader(mock_yaml).read_tree_from_yaml(file_path)

        self.assertEqual(values['name'], actual.name)
        self.assertEqual(values['checksum'], actual.checksum)
        self.assertEqual(values['checksum_algo'], actual.checksum_algo)
        self.assertEqual(values['size'], actual.size)

        mock_yaml.read_yaml_file.assert_called_once_with(file_path)

    @patch(fully_qualified_name(YamlSerialization))
    def test_read_tree_from_yaml_wraps_and_rethrows_exception(self, mock_yaml: YamlSerialization):
        expected_cause = 'expected_cause_message'
        mock_yaml.read_yaml_file = Mock(side_effect=Exception(expected_cause))

        file_path = Path(__file__)

        with self.assertRaises(InvalidScanFileException) as context:
            TreeLoader(mock_yaml).read_tree_from_yaml(file_path)

        self.assertTrue(expected_cause in str(context.exception), f'Expected error to contain root cause message: [{expected_cause}].')

    @patch(fully_qualified_name(Checksum))
    def test_read_tree_from_disk(self, mock_checksum: Checksum):
        checksum_algo = 'sha512'
        expected_checksum = 'expected_checksum_value'
        mock_checksum.compute_file_checksum = Mock(return_value=expected_checksum)

        test_asset_path = Path(__file__).absolute().parent.joinpath('tree_loader_test_assets')
        self.assertTrue(test_asset_path.is_dir(), f'Expected test assets to be in path [{test_asset_path}].')

        actual = TreeLoader(checksum=mock_checksum).read_tree_from_disk(test_asset_path, True, checksum_algo)

        self.assertIsNotNone(actual)

        self.assertIsNone(actual.parent)
        self.assertEqual(str(test_asset_path), actual.name)
        self.assertEqual(checksum_algo, actual.checksum_algo)
        self.assertIsNone(actual.checksum)

        child_nodes = either(actual.children, [])
        self.assertIsNotNone(child_nodes)
        self.assertEqual(1, len(child_nodes))

        self.assertEqual('test.txt', child_nodes[0].name)
        self.assertEqual(expected_checksum, child_nodes[0].checksum)
        self.assertIsNone(child_nodes[0].checksum_algo)
