from typing import List, Generator
from diff.tree import PathTree


def get_all_files_under_path(path_tree: PathTree) -> List[PathTree]:
    def yield_files_for_path(path_to_traverse: PathTree) -> Generator[PathTree, None, None]:
        if path_to_traverse.represents_directory():
            for child_path in path_to_traverse.children:
                yield from yield_files_for_path(child_path)
        else:
            yield path_to_traverse
    return list(yield_files_for_path(path_tree))
