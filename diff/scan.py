from __future__ import annotations
from pathlib import Path

import click

from diff.tree import build_path_tree, count_child_directories, count_child_files
from diff.tree.io import to_yaml_string
from diff.checksum import calculate_checksums_for_all_files_in_tree
from diff.util.decorators import log_exception, valid_path, PathType


@log_exception
@valid_path(PathType.Directory)
def _scan(folder: Path, output: str, checksum: bool):
    print(f'Scanning for files and folders in folder: [{folder}]')
    tree = build_path_tree(folder)

    if checksum:
        calculate_checksums_for_all_files_in_tree(tree)

    print(f'Saving scan results to: [{output}]')
    with open(output, 'w', encoding='utf-8') as file:
        file.write(to_yaml_string(tree))

    dir_count = count_child_directories(tree)
    file_count = count_child_files(tree)
    print('\n===== ===== ===== ===== =====\n')
    print(f'Finished scan. Found [{dir_count}] directories and [{file_count}] files.')
    print('\n===== ===== ===== ===== =====\n')


@click.command('scan')
@click.argument('folder')
@click.argument('output')
@click.option('--checksum', '-c', is_flag=True)
def scan(folder: str, output: str, checksum: bool):
    _scan(folder, output, checksum)
