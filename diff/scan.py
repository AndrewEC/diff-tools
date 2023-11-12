from pathlib import Path
import click

from diff.tree import read_tree_from_disk, to_yaml_file, read_tree_from_yaml, diff_between_trees


@click.command('folder')
@click.argument('path')
@click.argument('output')
@click.option('--checksum', '-c', is_flag=True, help='Specifies if the checksum should be calculated for'
                                                     ' each file found in the scan.')
def _folder(path: str, output: str, checksum: bool):
    """
    Scans a given directory and saves the results of the scan to a yaml file.

    path: The path to the directory to be scanned.

    output: The path where the yaml file containing the results of the scan should be saved to.
    """

    path_to_scan = Path(path).absolute()
    if not path_to_scan.is_dir():
        raise ValueError('The path to scan must be a directory. Current path is either not a directory or does not exist.')

    output_path = Path(output).absolute()
    if output_path.is_file():
        raise ValueError(f'The output path already exists. Delete the following file and try again: [{output_path}]')

    print(f'Scanning path: [{path_to_scan}]')
    root_node = read_tree_from_disk(path_to_scan, checksum)

    to_yaml_file(output_path, root_node)
    print(f'Scan results saved to: [{output_path}]')


@click.command('verify')
@click.argument('scan')
@click.option('--checksum', '-c', is_flag=True, help='Specifies if the checksum should be calculated for'
                                                     ' each file found in the scan.')
def _verify(scan: str, checksum: bool):
    """
    Checks if the results of a previous scan match what is currently on disk.

    This will check to see if any files have been deleted, added, or have changed either in terms of their size or
    their checksum.

    scan: The path to the yaml file containing the results of a previous scan.
    """

    scan_path = Path(scan).absolute()
    if not scan_path.is_file():
        raise ValueError('The scan path must point to the location of a previously saved scan.')

    scan_tree = read_tree_from_yaml(scan_path)
    root_path = scan_tree.path_to_node()
    if not root_path.is_dir():
        raise Exception(f'Could not verify scan because the original scanned directory could not be found at: [{root_path}]')

    disk_tree = read_tree_from_disk(root_path, checksum)
    diff_result = diff_between_trees(scan_tree, disk_tree)

    print('\n----- Similar -----')
    if len(diff_result.similar) > 0:
        print('The following files have the same path but different checksums or file sizes when compared to the same'
              ' path in the scan result.')
        for similar in diff_result.similar:
            print(f'\t[{similar[0].path_to_node()}]')
    else:
        print('No files with similar paths but different checksums or file sizes were found.')

    print('')

    print('----- Differences -----')
    if len(diff_result.first_tree.missing) > 0:
        print(f'The following files were found on disk but not in the previous scan result (new files):')
        for missing in diff_result.first_tree.missing:
            print(f'\t[{missing.path_to_node()}]')
    else:
        print(f'All files found on disk are also listed in the previous scan result.')

    print('')

    if len(diff_result.second_tree.missing) > 0:
        print(f'The following files were listed in the previous scan result but not on disk (deleted files):')
        for missing in diff_result.second_tree.missing:
            print(f'\t[{missing.path_to_node()}]')
    else:
        print(f'All files listed in the previous scan result were found on disk.')

    print('')


@click.group()
def scan():
    pass

scan.add_command(_verify)
scan.add_command(_folder)
