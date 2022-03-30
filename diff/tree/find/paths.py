from typing import List, Generator, Tuple, Optional

from .. import PathTree


def _path_without_root(path_tree: PathTree) -> str:
    return str(path_tree.path).replace(str(path_tree.get_root().path), '')


def _find_child_of_tree_with_similar_path(path_tree: PathTree, tree_to_match: PathTree) -> Optional[PathTree]:
    target_path_str = _path_without_root(tree_to_match)
    for child in path_tree.children:
        child_path_str = _path_without_root(child)
        if target_path_str == child_path_str:
            return child


def _are_paths_of_same_size(first: PathTree, second: PathTree) -> bool:
    return first.path.stat().st_size == second.path.stat().st_size


def find_similar_paths_between_trees(first_source_tree: PathTree, second_source_tree: PathTree, match_file_sizes=False) -> List[Tuple[PathTree, PathTree]]:
    def yield_similar(first_tree: PathTree, second_tree: PathTree) -> Generator[Tuple[PathTree, PathTree], None, None]:
        for first_tree_child in first_tree.children:
            second_tree_child = _find_child_of_tree_with_similar_path(second_tree, first_tree_child)
            if not second_tree_child or (match_file_sizes and not _are_paths_of_same_size(first_tree_child, second_tree_child)):
                continue
            if first_tree_child.represents_directory():
                yield from yield_similar(first_tree_child, second_tree_child)
            else:
                yield first_tree_child, second_tree_child
    return list(yield_similar(first_source_tree, second_source_tree))


def find_missing_paths_between_trees(first_source_tree: PathTree, second_source_tree: PathTree) -> List[PathTree]:
    def yield_missing(first_tree: PathTree, second_tree: PathTree) -> Generator[PathTree, None, None]:
        for first_child in first_tree.children:
            second_child = _find_child_of_tree_with_similar_path(second_tree, first_child)
            if not second_child:
                yield first_child
            else:
                yield from yield_missing(first_child, second_child)
    return list(yield_missing(first_source_tree, second_source_tree))
