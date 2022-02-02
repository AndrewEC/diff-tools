from typing import List, Tuple

from .. import PathTree
from ..find import find_similar_paths_between_trees


def find_changed_files(first: PathTree, second: PathTree) -> List[Tuple[PathTree, PathTree]]:
    similar_paths = find_similar_paths_between_trees(first, second)

    def are_checksums_same(to_compare: Tuple[PathTree, PathTree]) -> bool:
        first_match = to_compare[0]
        second_match = to_compare[1]

        if first_match.checksum is None or second_match.checksum is None:
            return True
        return first_match.checksum == second_match.checksum

    def are_files_different(similar_files: Tuple[PathTree, PathTree]) -> bool:
        return similar_files[0].size != similar_files[1].size or not are_checksums_same(similar_files)

    return list(filter(are_files_different, similar_paths))


def find_changed_files_take_first(first: PathTree, second: PathTree) -> List[PathTree]:
    return [different[0] for different in find_changed_files(first, second)]
