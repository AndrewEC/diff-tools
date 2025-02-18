from typing import List
from pathlib import Path

from diff.errors import InvalidScanFileException
from diff.util import compute_file_checksum

from .node import Node
from .yml import read_yaml_file

DEFAULT_HASH_ALGORITHM = 'sha256'

AVAILABLE_HASH_ALGORITHMS = [
    'sha1',
    DEFAULT_HASH_ALGORITHM,
    'sha512'
]

SKIPPABLE_FILES = [
]

SKIPPABLE_FOLDERS = [
    'System Volume Information',
    '$RECYCLE.BIN'
]


def read_tree_from_yaml(file_path: Path) -> Node:
    """
    Parses a yaml file to a dict and reads the dict into a Node instance that represents the root of the
    tree with all children attached.

    :param file_path: The path to the yaml file to read.
    :return: A Node instance deserialized from the yaml file content.
    """
    print(f'Reading contents of scan file: [{file_path}]')
    try:
        return Node.from_dict(None,  read_yaml_file(file_path))
    except Exception as e:
        raise InvalidScanFileException(file_path, e) from e


def _should_skip_file(path: Path) -> bool:
    return (
            (path.is_dir() and path.name in SKIPPABLE_FOLDERS)
            or (path.is_file() and path.name in SKIPPABLE_FILES)
    )


def _get_non_skippable_files(path: Path) -> List[Path]:
    all_files = path.iterdir()
    non_skippable_files = []
    for file in all_files:
        if _should_skip_file(file):
            print(f'Skipping file since it has an excluded name: [{file.name}]')
        else:
            non_skippable_files.append(file)
    return non_skippable_files


def read_tree_from_disk(path: Path, compute_checksums: bool, algo: str = None) -> Node:
    """
    Initializes a full Node tree from the contents of a path on disk.

    This will iterate through all nested elements within the input path and create Nodes representing each
    file and directory identified.

    If compute_checksums is specified as True then this will also compute the checksum of all files and attach
    said checksum to each Node representing said files.

    :param path: The path to the directory whose contents are to be scanned by this function.
    :param compute_checksums: If true this will compute the checksum of all files within the specified path.
    :param algo: The algorithm to use to compute the checksum of the files on disk.
    :return: The new Node instance initialized from the disk contents.
    """
    def attach_children(current_path: Path, current_node: Node):
        if not current_path.is_dir():
            return
        child_paths = _get_non_skippable_files(current_path)
        if len(child_paths) == 0:
            return
        for child_path in child_paths:
            checksum = None
            if compute_checksums and child_path.is_file():
                checksum = compute_file_checksum(child_path, algo)
            child_node = Node.from_disk(current_node, child_path, checksum, None)
            attach_children(child_path, child_node)

    print(f'Scanning contents of: [{path}]')
    root_node = Node.from_disk(None, path, None, algo, str(path))
    attach_children(path, root_node)
    return root_node
