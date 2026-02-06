from pathlib import Path

import unittest

from diff.core.util import Checksum


class ComputeFileChecksumTests(unittest.TestCase):

    def test_compute_file_checksum(self):
        test_cases = [
            ('sha256', 'B2E0377B4BC6AFDFBDEE3F8D700436721803827D82354CECEBD2226BFE6A7C69'),
            ('sha512', '50D27C29ADEEE3742FE258D1BC41AE60176491C7EE929AC0ACB56AFCE3D7D6E0AEAAC53633C54B701B0AC67C3FB1F32BFDB22EFE03A3674662B529AD52347E39')
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
