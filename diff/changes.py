from typing import List
from pathlib import Path

import click

from diff.tree import PathTree
import diff.tree as path_tree
from diff.util import extract_path_to_drive_letter
import diff.find as find


def _print_missing_files_and_folders(missing_paths: List[PathTree]):
    if len(missing_paths) == 0:
        return print('All files and directories still exist.')

    for missing_path in missing_paths:
        if missing_path.represents_directory():
            print(f'Missing directory and sub-directories of [{missing_path.path}].')
        else:
            print(f'Missing file: [{missing_path.path}]')


def _print_new_files_and_folders(new_paths: List[PathTree]):
    if len(new_paths) == 0:
        return print('No new files and directories were found on the drive.')

    for new_path in new_paths:
        if new_path.represents_directory():
            print(f'A new directory was found at: [{new_path.path}]')
        else:
            print(f'A new file was found at: [{new_path.path}].')


def _print_paths_with_changed_files(changed_paths: List[PathTree]):
    if len(changed_paths) == 0:
        return print('No changes in files could be found since last scan.')

    for path in changed_paths:
        print(f'The file [{path.path}] has changed since last scan.')


@click.command('changes')
@click.argument('scan')
@click.option('--checksum', '-c', is_flag=True)
def changes(scan: str, checksum: bool):
    if not Path(scan).is_file():
        raise Exception(f'The path [{scan}] either doesn\'t exist or does not point to a file.')

    with open(scan, 'r') as file:
        contents = '\n'.join(file.readlines())
    source_tree = path_tree.from_yaml_string(contents)

    drive_path = extract_path_to_drive_letter(source_tree)
    if not drive_path.is_dir():
        raise Exception(f'The scan results point to drive [{drive_path}] but the drive could not be found.')

    missing_paths = find.find_files_removed_since_last_scan(source_tree)
    new_paths = find.find_files_added_since_last_scan(source_tree)
    changed_paths = find.find_files_with_changes_since_last_scan(source_tree, checksum)

    print('\n===== ===== ===== ===== =====\n')
    _print_missing_files_and_folders(missing_paths)
    print('\n===== ===== ===== ===== =====\n')
    _print_new_files_and_folders(new_paths)
    print('\n===== ===== ===== ===== =====\n')
    _print_paths_with_changed_files(changed_paths)
    print('\n===== ===== ===== ===== =====\n')
