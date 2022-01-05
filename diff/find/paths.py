from typing import List, Generator, Tuple, Optional

from pathlib import Path

from diff.tree import PathTree
from diff.util import path_without_drive_letter


def _find_adjacent_child_with_similar_path(source_tree: PathTree, target_path: Path) -> Optional[PathTree]:
    target_path_str = path_without_drive_letter(target_path)
    for child in source_tree.children:
        child_path_str = path_without_drive_letter(child.path)
        if target_path_str == child_path_str:
            return child


def find_similar_paths_between_trees(first_source_tree: PathTree, second_source_tree: PathTree) -> List[Tuple[PathTree, PathTree]]:
    def yield_similar(first_tree: PathTree, second_tree: PathTree) -> Generator[Tuple[PathTree, PathTree], None, None]:
        for first_tree_child in first_tree.children:
            second_tree_child = _find_adjacent_child_with_similar_path(second_tree, first_tree_child.path)
            if not second_tree_child:
                continue
            if first_tree_child.represents_directory():
                yield from yield_similar(first_tree_child, second_tree_child)
            else:
                yield first_tree_child, second_tree_child
    return list(yield_similar(first_source_tree, second_source_tree))


def find_missing_paths_between_trees(first_source_tree: PathTree, second_source_tree: PathTree) -> List[PathTree]:
    def yield_missing(first_tree: PathTree, second_tree: PathTree) -> Generator[PathTree, None, None]:
        for first_child in first_tree.children:
            second_child = _find_adjacent_child_with_similar_path(second_tree, first_child.path)
            if not second_child:
                yield first_child
            else:
                yield from yield_missing(first_child, second_child)
    return list(yield_missing(first_source_tree, second_source_tree))
