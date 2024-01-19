from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import click

from diff.tree import read_tree_from_disk, diff_between_trees, DEFAULT_HASH_ALGORITHM, AVAILABLE_HASH_ALGORITHMS
from diff.errors import NotADirectoryException


@click.command()
@click.argument('first')
@click.argument('second')
@click.option('--checksum', '-c', is_flag=True, help='Specifies if the checksum should be calculated for'
                                                     ' each file found in the scan.')
@click.option('--algo', '-a', type=click.Choice(AVAILABLE_HASH_ALGORITHMS), default=DEFAULT_HASH_ALGORITHM, help='The preferred algorithm to hash the file with.')
def between(first: str, second: str, checksum: bool, algo: str):
    """
    Scans two directories, specified by the first and second paths, and compares the structure of the two.

    This will identify all files that are similar (have the same name but different size or checksum), all files
    that exist within the first directory but not the second, and all files that exist within the second directory but
    not the first.
    """

    first_path = Path(first).absolute()
    if not first_path.is_dir():
        raise NotADirectoryException('first path', first_path)

    second_path = Path(second).absolute()
    if not second_path.is_dir():
        raise NotADirectoryException('second path', second_path)

    if first == second:
        raise ValueError('The first path to scan and the second path to scan cannot refer to the same location.')

    with ThreadPoolExecutor(max_workers=2) as executor:
        first_execution = executor.submit(read_tree_from_disk, first_path, checksum, algo)
        second_execution = executor.submit(read_tree_from_disk, second_path, checksum, algo)
        first_tree = first_execution.result()
        second_tree = second_execution.result()
    diff_result = diff_between_trees(first_tree, second_tree)

    print('\n----- Similar -----')
    if len(diff_result.similar) > 0:
        print('The following files have the same path but different checksums or file sizes.')
        for similar in diff_result.similar:
            print(f'\t[{similar[0].path_to_node()}] -> [{similar[1].path_to_node()}]')
    else:
        print('No files with similar paths but different checksums or file sizes were found.')

    print('')

    print('----- Differences -----')
    if len(diff_result.first_tree.missing) > 0:
        print(f'The following files were found in [{second_tree.path_to_node()}] but not in [{first_tree.path_to_node()}]:')
        for missing in diff_result.first_tree.missing:
            print(f'\t[{missing.path_to_node()}]')
    else:
        print(f'All files found in [{second_tree.path_to_node()}] were also found in [{first_tree.path_to_node()}].')

    print('')

    if len(diff_result.second_tree.missing) > 0:
        print(f'The following files were found in [{first_tree.path_to_node()}] but not in [{second_tree.path_to_node()}]:')
        for missing in diff_result.second_tree.missing:
            print(f'\t[{missing.path_to_node()}]')
    else:
        print(f'All files found in [{first_tree.path_to_node()}] were also found in [{second_tree.path_to_node()}].')

    print('')
