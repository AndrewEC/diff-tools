from pathlib import Path

import unittest

from diff.core.util import Checksum


class ComputeFileChecksumTests(unittest.TestCase):

    def test_compute_file_checksum(self):
        test_cases = [
            ('sha256', 'b2e0377b4bc6afdfbdee3f8d700436721803827d82354cecebd2226bfe6a7c69'),
            ('sha512', '50d27c29adeee3742fe258d1bc41ae60176491c7ee929ac0acb56afce3d7d6e0aeaac53633c54b701b0ac67c3fb1f32bfdb22efe03a3674662b529ad52347e39')
        ]

        input_file_path = Path(__file__).absolute().parent.joinpath('checksum_test_file.txt')
        self.assertTrue(
            input_file_path.is_file(),
            f'Expected input test file to be in expected location of: [{input_file_path}].'
        )

        for test_case in test_cases:
            with self.subTest(algo=test_case[0]):
                actual = Checksum().compute_file_checksum(input_file_path, test_case[0])
                self.assertEqual(test_case[1], actual)
