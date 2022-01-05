from typing import List, Tuple

from diff.tree import PathTree, rebuild_tree_from_drive_contents
from diff.checksum import calculate_checksums_for_all_files_in_tree
from .paths import find_missing_paths_between_trees, find_similar_paths_between_trees


def find_files_removed_since_last_scan(source_tree: PathTree) -> List[PathTree]:
    drive_and_tree = rebuild_tree_from_drive_contents(source_tree)
    return find_missing_paths_between_trees(source_tree, drive_and_tree[1])


def find_files_added_since_last_scan(source_tree: PathTree) -> List[PathTree]:
    drive_and_tree = rebuild_tree_from_drive_contents(source_tree)
    return find_missing_paths_between_trees(drive_and_tree[1], source_tree)


def find_files_with_changes_since_last_scan(source_tree: PathTree, checksum: bool) -> List[PathTree]:
    drive_and_tree = rebuild_tree_from_drive_contents(source_tree)
    if checksum:
        print(f'Calculating checksums for files under path: [{drive_and_tree[0]}]')
        calculate_checksums_for_all_files_in_tree(drive_and_tree[1])
    return find_changed_files(source_tree, drive_and_tree[1], checksum)


def find_changed_files(first: PathTree, second: PathTree, checksum: bool) -> List[PathTree]:
    matched = find_similar_paths_between_trees(first, second)

    def compare_checksums(to_compare: Tuple[PathTree, PathTree]) -> bool:
        if not checksum:
            return False
        first_match = to_compare[0]
        second_match = to_compare[1]
        return first_match.checksum is not None and second_match.checksum is not None and first_match.checksum != second_match.checksum

    different = []
    for match in matched:
        if match[0].size != match[1].size or compare_checksums(match):
            different.append(match[0])
    return different
