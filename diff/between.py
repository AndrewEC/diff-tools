from typing import List, Tuple
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor

import click

from diff.tree import PathTree, build_path_tree
from diff.tree.io import from_yaml_file
from diff.tree.find import find_missing_paths_between_trees, find_similar_paths_between_trees, find_changed_files
from diff.util.decorators import valid_path, PathType, log_exception
from diff.checksum import calculate_checksums_of_two_trees, get_checksum_function, ChecksumFunctionType


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
        return print('All common files between folders appear to be the same.')

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


def _calculate_checksums_of_files(first: Path, second: Path, exact_hash: bool) -> List[str]:
    def do_calculate_checksum(file_path: Path) -> str:
        print(f'Calculating checksum of file: [{file_path}]')
        checksum_function = get_checksum_function(file_path, exact_hash)
        if checksum_function.function_type == ChecksumFunctionType.Pseudo:
            print(f'File [{file_path}] is over 200 megabytes. Checksum will be calculated as a pseudo checksum.')
        return checksum_function.apply(file_path)

    with ThreadPoolExecutor(2) as executor:
        return list(executor.map(do_calculate_checksum, [first, second]))


@log_exception('Could not finish scanning both input folders.')
@valid_path(PathType.Directory, PathType.Directory)
def _do_between_folders(first_folder_path: Path, second_folder_path: Path, checksum: bool):
    if first_folder_path == second_folder_path:
        raise Exception('Both paths point to the same directory. This utility should be used to find the differences '
                        'between two different directories.')
    with ThreadPoolExecutor(2) as executor:
        trees = list(executor.map(build_path_tree, [first_folder_path, second_folder_path]))
    first_tree = trees[0]
    second_tree = trees[1]

    if checksum:
        _calculate_checksums_of_similar_files(first_tree, second_tree)

    _find_and_print_changes(first_tree, second_tree)


@log_exception('Could not detect all changes between scans.')
@valid_path(PathType.File, PathType.File)
def _do_between_scans(first_scan_path: Path, second_scan_path: Path):
    if first_scan_path == second_scan_path:
        raise Exception('Both paths point to the same file. This utility should be used to verify the differences '
                        'between two different scan results.')
    first_tree = from_yaml_file(first_scan_path)
    second_tree = from_yaml_file(second_scan_path)
    _find_and_print_changes(first_tree, second_tree)


@log_exception('Could not compute fingerprints for both files.')
@valid_path(PathType.File, PathType.File)
def _do_between_files(first_file: Path, second_file: Path, exact_hash: bool):
    if first_file == second_file:
        return print('Both paths point to the same file. This utility should be used to check the differences'
                     ' between two files. Use the checksum utility to calculate the checksum of a single file.')
    first_file_checksum, second_file_checksum = _calculate_checksums_of_files(first_file, second_file, exact_hash)
    if first_file_checksum != second_file_checksum:
        print('The checksums of the files do not match.')
    else:
        print('Both files have the same checksums.')
    print(f'[{first_file}] :: [{first_file_checksum}]')
    print(f'[{second_file}] :: [{second_file_checksum}]')


@click.command('folders')
@click.argument('first_folder')
@click.argument('second_folder')
@click.option('--checksum', '-c', is_flag=True)
def _between_folders(first_folder: str, second_folder: str, checksum: bool):
    """
    Scans two folders and prints the differences between the two.

    This will compare all child files and folders within the specified folders and print all files/folders that exist
    under one folder but not the other or if two files have a different file size or SHA hash.
    """
    _do_between_folders(first_folder, second_folder, checksum)


@click.command('scans')
@click.argument('first_scan')
@click.argument('second_scan')
def _between_scans(first_scan: str, second_scan: str):
    """
    Compares two scan results and prints the differences between them.

    This will compare all child files and folders within the specified folders and print all files/folders that exist
    under one folder but not the other or if two files have a different file size or SHA hash.

    This won't actually scan the files on disk. Rather, it just relies on the files and checksums listed in the scan
    results. If either of the scan results doesn't contain the SHA hash of the files then no checksum comparison
    will be made.s
    """
    _do_between_scans(first_scan, second_scan)


@click.command('files')
@click.argument('first_file')
@click.argument('second_file')
@click.option('--exact-hash', '-e', is_flag=True)
def _between_files(first_file: str, second_file: str, exact_hash: bool):
    """
    Compares two files to determine if they are the same.

    By default this will only check if the size of the files match. If the --exact-hash argument is provided then
    this will also compute and compare a SHA hash of each file.
    """
    _do_between_files(first_file, second_file, exact_hash)


@click.group('between')
def between_group():
    pass


between_group.add_command(_between_folders)
between_group.add_command(_between_scans)
between_group.add_command(_between_files)
