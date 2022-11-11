from typing import List, Generator, Tuple, Optional

from .. import PathTree


def _path_without_root(path_tree: PathTree) -> str:
    return str(path_tree.path).replace(str(path_tree.get_root().path), '')


def _find_child_of_tree_with_similar_path(path_tree: PathTree, tree_to_match: PathTree) -> Optional[PathTree]:
    target_path_str = _path_without_root(tree_to_match)
    return next((child for child in path_tree.children if _path_without_root(child) == target_path_str), None)


def _are_files_of_same_size(first: PathTree, second: PathTree) -> bool:
    return first.path.stat().st_size == second.path.stat().st_size


def find_similar_paths_between_trees(first_source_tree: PathTree, second_source_tree: PathTree, match_file_sizes=False) -> List[Tuple[PathTree, PathTree]]:
    """
    Returns a list of tuples in which each tuple represents two files that have a similar path. To determine if two
    file paths are similar this will remove the path represented by the root node of the PathTree from the files
    absolute path and check if it matches another path in the second path tree.

    For example:
    The first path tree has a root of C:/ and a file with the absolute path of C:/Testing/123.png
    The second path tree has a root of D:/ and a file with the absolute path of D:/Testing/123.png
    If we remove the root from both paths we get Testing/123.png and Testing/123.png which means these two files
    are considered similar from the perspective of their paths.

    :param first_source_tree: The first tree to traverse. From this tree we will pull all the files and their paths
    and sizes to check against the second tree.
    :param second_source_tree: The second tree. The files identified in the first tree will be looked up in the
    second tree.
    :param match_file_sizes: If true indicates that the file paths must be similar but their file sizes must also be
    the same.
    :return: A list of tuples representing the files that have been identified as being similar to a file in the
    second tree.
    """
    def yield_similar(first_tree: PathTree, second_tree: PathTree) -> Generator[Tuple[PathTree, PathTree], None, None]:
        for first_tree_child in first_tree.children:
            second_tree_child = _find_child_of_tree_with_similar_path(second_tree, first_tree_child)
            if not second_tree_child or (match_file_sizes and not _are_files_of_same_size(first_tree_child, second_tree_child)):
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
