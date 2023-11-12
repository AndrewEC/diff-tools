from pathlib import Path

import click

from diff.tree import read_tree_from_disk, diff_between_trees


@click.command()
@click.argument('first')
@click.argument('second')
@click.option('--checksum', '-c', is_flag=True, help='Specifies if the checksum should be calculated for'
                                                     ' each file found in the scan.')
def between(first: str, second: str, checksum: bool):
    """
    Scans two directories, specified by the first and second paths, and compares the structure of the two.

    This will identify all files that are similar (have the same name but different size or checksum), all files
    that exist within the first directory but not the second, and all files that exist within the second directory but
    not the first.
    """

    first_path = Path(first).absolute()
    if not first_path.is_dir():
        raise ValueError('The first path to scan must point to a directory. The first path is either not a directory or does not exist.')

    second_path = Path(second).absolute()
    if not second_path.is_dir():
        raise ValueError('The second path to scan must point to a directory. The second path is either not a directory or does not exist.')

    if first == second:
        raise ValueError('The first path to scan and the second path to scan cannot refer to the same location.')

    first_tree = read_tree_from_disk(first_path, checksum)
    second_tree = read_tree_from_disk(second_path, checksum)
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
