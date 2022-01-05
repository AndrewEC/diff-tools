from typing import List, Generator
from concurrent.futures import ThreadPoolExecutor, as_completed

from diff.tree import PathTree
from .functions import calculate_checksum


_MAX_TASK_COUNT = 3


def _get_all_files_under_path(path_tree: PathTree) -> List[PathTree]:
    def yield_files_for_path(path_to_traverse: PathTree) -> Generator[PathTree, None, None]:
        if path_to_traverse.represents_directory():
            for child_path in path_to_traverse.children:
                yield from yield_files_for_path(child_path)
        else:
            yield path_to_traverse
    return list(yield_files_for_path(path_tree))


def calculate_checksums(trees: List[PathTree]):
    task_count = min(len(trees), _MAX_TASK_COUNT)

    def task(file: PathTree):
        file.checksum = calculate_checksum(file.path)

    with ThreadPoolExecutor(max_workers=task_count) as executor:
        future_results = list(map(lambda argument: executor.submit(task, argument), trees))
        [future.result() for future in as_completed(future_results)]


def calculate_checksums_for_all_files_in_tree(path_tree: PathTree):
    files_under_path = _get_all_files_under_path(path_tree)
    print(f'Calculating checksum for [{len(files_under_path)}] files')
    calculate_checksums(files_under_path)


def calculate_checksums_of_two_trees(first_tree_paths: List[PathTree], second_tree_paths: List[PathTree]):
    with ThreadPoolExecutor(2) as executor:
        executor.map(calculate_checksums, [first_tree_paths, second_tree_paths])
