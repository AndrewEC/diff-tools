from typing import List, Tuple
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor

import click

from diff.tree import PathTree, build_path_tree
from diff.tree.io import from_yaml_file
from diff.tree.find import find_missing_paths_between_trees, find_similar_paths_between_trees, find_changed_files
from diff.util.decorators import valid_path, PathType, log_exception
from diff.checksum import calculate_checksums_of_two_trees


def _print_missing_files_and_folders(missing_paths: List[PathTree], first_folder: Path, second_folder: Path):
    if len(missing_paths) == 0:
        return print(f'All files in folder [{first_folder}] were found in [{second_folder}].')

    for missing_path in missing_paths:
        if missing_path.represents_directory():
            print(f'Directory found at [{missing_path.path}] is missing from [{second_folder}]')
        else:
            print(f'File found at [{missing_path.path}] is missing from [{second_folder}]')


def _print_changed_files(differences: List[Tuple[PathTree, PathTree]]):
    if len(differences) == 0:
        print('All common files between folders appear to be the same.')

    for difference in differences:
        print(f'Two similarly named files that contain different contents were found:')
        for diff in difference:
            print(f'\t[{diff.path}]')


def _calculate_checksums_of_similar_files(first_tree: PathTree, second_tree: PathTree):
    def similar_paths_at_index(index: int, similar: List[Tuple[PathTree, PathTree]]) -> List[PathTree]:
        return [path_tree[index] for path_tree in similar]

    similar_paths = find_similar_paths_between_trees(first_tree, second_tree, True)
    first_tree_paths = similar_paths_at_index(0, similar_paths)
    second_tree_paths = similar_paths_at_index(1, similar_paths)
    print(f'Calculating checksums for [{len(similar_paths)}] files common between both folders.')
    calculate_checksums_of_two_trees(first_tree_paths, second_tree_paths)


def _find_and_print_changes(first_tree: PathTree, second_tree: PathTree):
    first_missing = find_missing_paths_between_trees(first_tree, second_tree)
    second_missing = find_missing_paths_between_trees(second_tree, first_tree)
    changed_files = find_changed_files(first_tree, second_tree)

    print('\n===== ===== ===== ===== =====\n')
    _print_missing_files_and_folders(first_missing, first_tree.path, second_tree.path)
    print('\n===== ===== ===== ===== =====\n')
    _print_missing_files_and_folders(second_missing, second_tree.path, first_tree.path)
    print('\n===== ===== ===== ===== =====\n')
    _print_changed_files(changed_files)
    print('\n===== ===== ===== ===== =====\n')


@log_exception
@valid_path(PathType.Directory, PathType.Directory)
def _do_between_folders(first_folder_path: Path, second_folder_path: Path, checksum: bool):
    if first_folder_path == second_folder_path:
        return print('Both paths point to the same directory. This utility should be used to find the differences '
                     'between two different directories.')
    with ThreadPoolExecutor(2) as executor:
        trees = list(executor.map(build_path_tree, [first_folder_path, second_folder_path]))
    first_tree = trees[0]
    second_tree = trees[1]

    if checksum:
        _calculate_checksums_of_similar_files(first_tree, second_tree)

    _find_and_print_changes(first_tree, second_tree)


@log_exception
@valid_path(PathType.File, PathType.File)
def _do_between_scans(first_scan_path: Path, second_scan_path: Path):
    first_tree = from_yaml_file(first_scan_path)
    second_tree = from_yaml_file(second_scan_path)
    _find_and_print_changes(first_tree, second_tree)


@click.command('folders')
@click.argument('first_folder')
@click.argument('second_folder')
@click.option('--checksum', '-c', is_flag=True)
def _between_folders(first_folder: str, second_folder: str, checksum: bool):
    _do_between_folders(first_folder, second_folder, checksum)


@click.command('scans')
@click.argument('first_scan')
@click.argument('second_scan')
def _between_scans(first_scan: str, second_scan: str):
    _do_between_scans(first_scan, second_scan)


@click.group('between')
def between_group():
    pass


between_group.add_command(_between_folders)
between_group.add_command(_between_scans)
