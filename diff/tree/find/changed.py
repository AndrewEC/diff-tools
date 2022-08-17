from typing import List, Tuple

from .. import PathTree
from ..find import find_similar_paths_between_trees


def find_changed_files(first: PathTree, second: PathTree) -> List[Tuple[PathTree, PathTree]]:
    """
    Finds the files that have changed between two PathTrees. This will check that two files are the same size
    and, if they are the same size, will then try to compare the previously computed checksums of each file. This
    does not compute the checksum of a file. The checksum must already be computed. If, at any time, either of
    two similar files do not have any checksums computed then the checksum check will effectively be skipped.

    This only compares files that exist within the first tree that also exist within the second tree. If a file,
    that exists in the first tree, does not exist in the second tree this function will effectively make no mention
    of that difference.

    :param first: The first path tree to traverse.
    :param second: The second path tree to traverse.
    :return: A list of tuples in which each tuple represents two files that were compared and found to have similar
    paths but ultimately had a different file size or checksum.
    """
    similar_paths = find_similar_paths_between_trees(first, second)

    def are_checksums_same(to_compare: Tuple[PathTree, PathTree]) -> bool:
        first_match = to_compare[0]
        second_match = to_compare[1]

        if first_match.checksum is None or second_match.checksum is None:
            return True
        return first_match.checksum == second_match.checksum

    def are_files_different(to_compare: Tuple[PathTree, PathTree]) -> bool:
        return to_compare[0].size != to_compare[1].size or not are_checksums_same(to_compare)

    return list(filter(are_files_different, similar_paths))


def find_changed_files_take_first(first: PathTree, second: PathTree) -> List[PathTree]:
    return [different[0] for different in find_changed_files(first, second)]
