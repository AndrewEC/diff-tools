from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

from diff.tree import PathTree
from diff.util import get_all_files_under_path
from .functions import get_checksum_function, ChecksumFunctionType


_MAX_TASK_COUNT = 3


def calculate_checksums(trees: List[PathTree]):
    task_count = min(len(trees), _MAX_TASK_COUNT)

    def task(file: PathTree):
        print(f'Calculating checksum of file: [{file.path}]')
        checksum_function = get_checksum_function(file.path)
        if checksum_function.function_type == ChecksumFunctionType.Pseudo:
            print(f'File [{file.path}] is over 200 megabytes. Checksum will be calculated as a pseudo checksum.')
        file.checksum = checksum_function.apply(file.path)

    with ThreadPoolExecutor(max_workers=task_count) as executor:
        future_results = list(map(lambda argument: executor.submit(task, argument), trees))
        [future.result() for future in as_completed(future_results)]


def calculate_checksums_for_all_files_in_tree(path_tree: PathTree):
    files_under_path = get_all_files_under_path(path_tree)
    print(f'Calculating checksum for [{len(files_under_path)}] files')
    calculate_checksums(files_under_path)


def calculate_checksums_of_two_trees(first_tree_paths: List[PathTree], second_tree_paths: List[PathTree]):
    with ThreadPoolExecutor(2) as executor:
        executor.map(calculate_checksums, [first_tree_paths, second_tree_paths])
