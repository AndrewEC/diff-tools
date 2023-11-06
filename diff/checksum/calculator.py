from typing import List
from concurrent.futures import ThreadPoolExecutor

from diff.tree import PathTree
from diff.util import get_all_files_under_path
from .functions import get_checksum_function, ChecksumFunctionType


_MAX_TASK_COUNT = 3


def calculate_checksums(trees: List[PathTree]):
    """
    Calculates the checksums of all files represented by a PathTree instance from the input list. This will mutate
    each PathTree instance by setting the checksum property. This checksum will only be calculated and applied
    to files and not folders.

    This is a multithreaded function and will use a thread pool executor with a maximum of 3 threads to calculate the
    checksums of each file.

    :param trees:  The list of all the PathTrees containing the location of the files whose checksums need to be
    calculated.
    """
    task_count = min(len(trees), _MAX_TASK_COUNT)

    def task(file: PathTree):
        print(f'Calculating checksum of file: [{file.path}]')
        try:
            checksum_function = get_checksum_function(file.path)
            if checksum_function.function_type == ChecksumFunctionType.Pseudo:
                print(f'File [{file.path}] is over 200 megabytes. Checksum will be calculated as a pseudo checksum.')
            file.checksum = checksum_function.apply(file.path)
        except Exception as e:
            print(f'Could not calculate checksum of file [{file.path}]. Cause: [{e}]')

    with ThreadPoolExecutor(max_workers=task_count) as executor:
        executor.map(task, trees)


def calculate_checksums_for_all_files_in_tree(path_tree: PathTree):
    """
    Combs through the input path tree instance, aggregates all the child files of the path tree, then concurrently
    calculates the checksums of all the files.

    :param path_tree: The root path from which we will pull all the child file paths and compute their checksums.
    """
    files_under_path = get_all_files_under_path(path_tree)
    file_count = len(files_under_path)
    print(f'Calculating checksum for [{file_count}] files')
    if file_count == 0:
        return
    calculate_checksums(files_under_path)


def calculate_checksums_of_two_trees(first_tree_paths: List[PathTree], second_tree_paths: List[PathTree]):
    """
    Concurrently calculates the checksums of all files specified within the two provided PathTree instances.

    :param first_tree_paths: The first tree whose file checksums will be calculated.
    :param second_tree_paths: The second tree whose file checksums will be calculated.
    """
    with ThreadPoolExecutor(2) as executor:
        executor.map(calculate_checksums, [first_tree_paths, second_tree_paths])
