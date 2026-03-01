from pathlib import Path
import unittest
from unittest.mock import Mock, patch, call

from diff.core.cli import CliChecksum
from diff.core.util import Checksum
from diff.core.errors import NotAFileException

from diff.tests.util import fully_qualified_name


class CliChecksumTests(unittest.TestCase):

    @patch(fully_qualified_name(Checksum))
    def test_calculate(self, mock_checksum: Checksum):
        expected_checksum = 'expected_checksum_value'
        checksum_algo = 'sha256'

        mock_print_function = Mock()
        mock_checksum.compute_file_checksum = Mock(return_value=expected_checksum)

        file_path = Path(__file__)

        CliChecksum(mock_checksum, mock_print_function).calculate(str(file_path), checksum_algo)

        mock_checksum.compute_file_checksum.assert_called_once_with(file_path, checksum_algo)
        mock_print_function.assert_called_once_with('The sha256 file hash is: expected_checksum_value')

    @patch(fully_qualified_name(Checksum))
    def test_calculate_with_missing_file_raises_exception(self, mock_checksum: Checksum):
        checksum_algo = 'sha256'

        mock_checksum.compute_file_checksum = Mock()
        mock_print_function = Mock()

        file_path = Path(__file__).parent.joinpath('missing_file.txt')

        with self.assertRaises(NotAFileException) as context:
            CliChecksum(mock_checksum, mock_print_function).calculate(str(file_path), checksum_algo)

        self.assertTrue('does not point to a file' in str(context.exception))

        mock_checksum.compute_file_checksum.assert_not_called()
        mock_print_function.assert_not_called()

    @patch(fully_qualified_name(Checksum))
    def test_verify_with_matching_hashes(self, mock_checksum: Checksum):
        expected_checksum = 'EXPECTED_CHECKSUM_VALUE'
        checksum_algo = 'sha256'

        mock_checksum.compute_file_checksum = Mock(return_value=expected_checksum)
        mock_print_function = Mock()

        file_path = Path(__file__)

        CliChecksum(mock_checksum, mock_print_function).verify(str(file_path), expected_checksum, checksum_algo)

        mock_checksum.compute_file_checksum.assert_called_once_with(file_path, checksum_algo)
        mock_print_function.assert_called_once_with('The calculated file hash and the existing provided hash match.')

    @patch(fully_qualified_name(Checksum))
    def test_verify_with_different_hashes(self, mock_checksum: Checksum):
        existing_hash = 'DIFFERENT_CHECKSUM_VALUE'
        expected_checksum = 'expected_checksum_value'
        checksum_algo = 'sha256'

        mock_checksum.compute_file_checksum = Mock(return_value=expected_checksum)
        mock_print_function = Mock()

        file_path = Path(__file__)

        CliChecksum(mock_checksum, mock_print_function).verify(str(file_path), existing_hash, checksum_algo)

        mock_checksum.compute_file_checksum.assert_called_once_with(file_path, checksum_algo)
        mock_print_function.assert_has_calls([
            call('The calculated file has and the existing hash do not match.'),
            call('Hashes are:'),
            call(f'\tExisting: {existing_hash}'),
            call(f'\tComputed: {expected_checksum}')
        ])
    
    @patch(fully_qualified_name(Checksum))
    def test_compare_with_same_hashes(self, mock_checksum: Checksum):
        first_path = Path(__file__)
        second_path = Path(__file__).absolute().parent.joinpath('cli_between_test.py')
        checksum_algo = 'sha256'
        expected_hash = 'sha256_hash'

        mock_checksum.compute_file_checksum = Mock(return_value=expected_hash)
        mock_print_function = Mock()

        CliChecksum(mock_checksum, mock_print_function).compare(str(first_path), str(second_path), checksum_algo)

        mock_checksum.compute_file_checksum.assert_has_calls([
            call(first_path, checksum_algo),
            call(second_path, checksum_algo)
        ])

        mock_print_function.assert_has_calls([
            call(f'Both files have the same {checksum_algo} hash.'),
            call(f'The hash of both files is: {expected_hash}')
        ])
    
    @patch(fully_qualified_name(Checksum))
    def test_compare_with_different_hashes(self, mock_checksum: Checksum):
        first_path = Path(__file__)
        second_path = Path(__file__).absolute().parent.joinpath('cli_between_test.py')
        checksum_algo = 'sha256'

        first_hash = 'sha256_hash'
        second_hash = 'sha256_hash_different'

        mock_checksum.compute_file_checksum = Mock(side_effect=[first_hash, second_hash])
        mock_print_function = Mock()

        CliChecksum(mock_checksum, mock_print_function).compare(str(first_path), str(second_path), checksum_algo)

        mock_checksum.compute_file_checksum.assert_has_calls([
            call(first_path, checksum_algo),
            call(second_path, checksum_algo)
        ])

        mock_print_function.assert_has_calls([
            call(f'The files have different {checksum_algo} hashes.'),
            call(f'\t{first_path} -> {first_hash}'),
            call(f'\t{second_path} -> {second_hash}')
        ])

    @patch(fully_qualified_name(Checksum))
    def test_compare_with_same_paths(self, mock_checksum: Checksum):
        first_path = str(Path(__file__))

        with self.assertRaises(ValueError) as context:
            CliChecksum(mock_checksum, Mock()).compare(first_path, first_path, 'sha256')

        self.assertEqual(str(context.exception), 'The first file path and the second file path cannot refer to the same file. Specify different files and try again.')
    
    @patch(fully_qualified_name(Checksum))
    def test_compare_with_invalid_path(self, mock_checksum: Checksum):
        path = Path(__file__).absolute().parent.joinpath('missing_file.py')

        with self.assertRaises(NotAFileException) as context:
            CliChecksum(mock_checksum, Mock()).compare(str(path), str(path), 'sha256')

        self.assertEqual(str(context.exception), f'The path argument [first] does not point to a file. Please check the path and try again: [{path}]')
