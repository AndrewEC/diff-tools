from typing import List, Tuple

from .. import PathTree
from ..find import find_similar_paths_between_trees


def find_changed_files(first: PathTree, second: PathTree) -> List[PathTree]:
    matched = find_similar_paths_between_trees(first, second)

    def are_checksums_same(to_compare: Tuple[PathTree, PathTree]) -> bool:
        first_match = to_compare[0]
        second_match = to_compare[1]

        if first_match.checksum is None or second_match.checksum is None:
            return True
        return first_match.checksum == second_match.checksum

    different = []
    for match in matched:
        if match[0].size != match[1].size or not are_checksums_same(match):
            different.append(match[0])
    return different
