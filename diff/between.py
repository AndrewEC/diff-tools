from typing import List, Tuple
from pathlib import Path

import click

from diff.tree import PathTree, build_path_tree
from diff.find import find_missing_paths_between_trees, find_changed_files, find_similar_paths_between_trees
from diff.checksum import calculate_checksums_of_two_trees
from diff.util import path_without_drive_letter


def _print_missing_files_and_folders(missing_paths: List[PathTree], first_drive: Path, second_drive: Path):
    if len(missing_paths) == 0:
        return print(f'All files in drive [{first_drive}] were found in [{second_drive}].')

    for missing_path in missing_paths:
        if missing_path.represents_directory():
            print(f'Directory found at [{missing_path.path}] is missing from drive [{second_drive}]')
        else:
            print(f'File found at [{missing_path.path}] is missing from drive [{second_drive}]')


def _print_changed_files(differences: List[PathTree]):
    if len(differences) == 0:
        print('No files find were found.')

    for difference in differences:
        print(f'Both drives contain a file at [{path_without_drive_letter(difference.path)}] but they are different')


def _calculate_checksums(first_tree: PathTree, second_tree: PathTree):
    def similar_paths_at_index(index: int, similar: List[Tuple[PathTree, PathTree]]) -> List[PathTree]:
        return [path_tree[index] for path_tree in similar if path_tree[0].path.stat().st_size != path_tree[1].path.stat().st_size]

    similar_paths = find_similar_paths_between_trees(first_tree, second_tree)
    first_tree_paths = similar_paths_at_index(0, similar_paths)
    second_tree_paths = similar_paths_at_index(1, similar_paths)
    print(f'Calculating checksums for [{len(similar_paths)}] files common between both drives.')
    calculate_checksums_of_two_trees(first_tree_paths, second_tree_paths)


@click.command('between')
@click.argument('first_drive')
@click.argument('second_drive')
@click.option('--checksum', '-c', is_flag=True)
def between(first_drive: str, second_drive: str, checksum: bool):
    first_drive_path = Path(first_drive)
    second_drive_path = Path(second_drive)

    if not first_drive_path.is_dir():
        raise Exception(f'The path [{first_drive}] does not point to a file or the path does not exist.')

    if not second_drive_path.is_dir():
        raise Exception(f'The path [{second_drive}] does not point to a file or the path does not exist.')

    first_tree = build_path_tree(first_drive_path)
    second_tree = build_path_tree(second_drive_path)

    if checksum:
        _calculate_checksums(first_tree, second_tree)

    first_missing = find_missing_paths_between_trees(first_tree, second_tree)
    second_missing = find_missing_paths_between_trees(second_tree, first_tree)
    changed_files = find_changed_files(first_tree, second_tree, checksum)

    print('\n===== ===== ===== ===== =====\n')
    _print_missing_files_and_folders(first_missing, first_drive_path, second_drive_path)
    print('\n===== ===== ===== ===== =====\n')
    _print_missing_files_and_folders(second_missing, second_drive_path, first_drive_path)
    print('\n===== ===== ===== ===== =====\n')
    _print_changed_files(changed_files)
    print('\n===== ===== ===== ===== =====\n')