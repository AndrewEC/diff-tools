from __future__ import annotations
from pathlib import Path

import click

from diff.tree import build_path_tree, count_child_directories, count_child_files
from diff.tree.io import to_yaml_file
from diff.checksum import calculate_checksums_for_all_files_in_tree
from diff.util.decorators import log_exception, valid_path, PathType


@log_exception('The scan encountered an error.')
@valid_path(PathType.Directory)
def _scan(folder: Path, output: str, checksum: bool):
    print(f'Scanning directory: [{folder}]')
    tree = build_path_tree(folder)

    if checksum:
        calculate_checksums_for_all_files_in_tree(tree)

    dir_count = count_child_directories(tree)
    file_count = count_child_files(tree)
    print('\n===== ===== ===== ===== =====\n')
    print(f'Finished scan. Found [{dir_count}] directories and [{file_count}] files.')
    print(f'Saving yml results to: [{output}]')
    to_yaml_file(output, tree)
    print('\n===== ===== ===== ===== =====\n')


@click.command('scan')
@click.argument('folder')
@click.argument('output')
@click.option('--checksum', '-c', is_flag=True)
def scan_command(folder: str, output: str, checksum: bool):
    """
    Scans a given folder and dumps the files, sizes, and checksums to a YAML file.

    This will recursively scan all child files and directories of the specified folder.
    """
    _scan(folder, output, checksum)
