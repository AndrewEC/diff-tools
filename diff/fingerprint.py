from pathlib import Path

import click

import diff.checksum as check


@click.command('checksum')
@click.argument('file')
def fingerprint(file: str):
    file_path = Path(file)
    if not file_path.is_file():
        raise Exception('The input path either doesn\'t exist or does\'t point to a file.')

    checksum_string = check.calculate_checksum(file_path)

    print('\n===== ===== ===== ===== =====\n')
    print(f'Checksum of file is:\n\t{checksum_string}')
    print('\n===== ===== ===== ===== =====\n')
