from __future__ import annotations
from pathlib import Path

import click

import diff.tree as path_tree
from diff.checksum import calculate_checksums_for_all_files_in_tree


@click.command('scan')
@click.argument('drive')
@click.argument('output')
@click.option('--checksum', '-c', is_flag=True)
def scan(drive: str, output: str, checksum: bool):
    print(f'Scanning for list of existing files under path: [{drive}]')
    root_path = Path(drive)
    if not root_path.is_dir():
        raise Exception(f'The value provided for directory, [{drive}], must point to a readable directory.')
    tree = path_tree.build_path_tree(root_path)

    if checksum:
        print(f'Calculating checksums for files under path: [{root_path}]')
        calculate_checksums_for_all_files_in_tree(tree)

    print(f'Saving scan results to: [{output}]')
    with open(output, 'w', encoding='utf-8') as file:
        file.write(path_tree.to_yaml_string(tree))

    dir_count = path_tree.count_child_directories(tree)
    file_count = path_tree.count_child_files(tree)
    print('\n===== ===== ===== ===== =====\n')
    print(f'Finished scan. Found [{dir_count}] directories and [{file_count}] files.')
    print('\n===== ===== ===== ===== =====\n')
