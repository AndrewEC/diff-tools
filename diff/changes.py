from typing import List
from pathlib import Path

import click

from diff.util import extract_path_to_drive_letter
from diff.util.decorators import FILE, DIRECTORY, valid_path, log_exception
from diff.tree import PathTree, rebuild_tree_from_drive_contents
from diff.tree.io import from_yaml_string
from diff.tree.find import find_changed_files
from diff.checksum import calculate_checksums
from diff.tree.find import find_missing_paths_between_trees, find_similar_paths_between_trees


def _find_files_removed_since_last_scan(source_tree: PathTree, override: Path) -> List[PathTree]:
    drive_and_tree = rebuild_tree_from_drive_contents(source_tree, override)
    return find_missing_paths_between_trees(source_tree, drive_and_tree[1])


def _find_files_added_since_last_scan(source_tree: PathTree, override: Path) -> List[PathTree]:
    drive_and_tree = rebuild_tree_from_drive_contents(source_tree, override)
    return find_missing_paths_between_trees(drive_and_tree[1], source_tree)


def _find_files_with_changes_since_last_scan(source_tree: PathTree, checksum: bool, override: Path) -> List[PathTree]:
    drive_and_tree = rebuild_tree_from_drive_contents(source_tree, override)
    if checksum:
        similar_paths = find_similar_paths_between_trees(source_tree, drive_and_tree[1], True)
        print(f'Calculating checksums for [{len(similar_paths)}] files')
        paths_to_calculate = [paths[1] for paths in similar_paths]
        calculate_checksums(paths_to_calculate)
    return find_changed_files(source_tree, drive_and_tree[1])


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
            print(f'A new file was found at: [{new_path.path}]')


def _print_paths_with_changed_files(changed_paths: List[PathTree]):
    if len(changed_paths) == 0:
        return print('No changes in files could be found since last scan.')

    for path in changed_paths:
        print(f'The file [{path.path}] has changed since last scan.')


@log_exception
@valid_path(FILE, DIRECTORY)
def _changes(scan_results: Path, checksum: bool, override: Path):
    with open(scan_results, 'r') as file:
        contents = '\n'.join(file.readlines())
    source_tree = from_yaml_string(contents)

    drive_path = extract_path_to_drive_letter(source_tree)
    if not drive_path.is_dir():
        raise Exception(f'The scan results point to drive [{drive_path}] but the drive could not be found.')

    missing_paths = _find_files_removed_since_last_scan(source_tree, override)
    new_paths = _find_files_added_since_last_scan(source_tree, override)
    changed_paths = _find_files_with_changes_since_last_scan(source_tree, checksum, override)

    print('\n===== ===== ===== ===== =====\n')
    _print_missing_files_and_folders(missing_paths)
    print('\n===== ===== ===== ===== =====\n')
    _print_new_files_and_folders(new_paths)
    print('\n===== ===== ===== ===== =====\n')
    _print_paths_with_changed_files(changed_paths)
    print('\n===== ===== ===== ===== =====\n')


@click.command('changes')
@click.argument('scan')
@click.option('--checksum', '-c', is_flag=True)
@click.option('--override', '-o')
def changes(scan: str, checksum: bool, override: str):
    _changes(scan, checksum, override)
