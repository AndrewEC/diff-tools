from typing import List
from pathlib import Path
import hashlib

from .node import Node
from .yml import read_yaml_file


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
        raise Exception(f'Could not parse previous scan yml file. Cause: [{e}]', e)


def compute_file_hash(path: Path, algo: str = 'sha256') -> str:
    if not path.is_file():
        print(f'Could not compute hash because path does not point to a file: [{path}]')
        return ''
    print(f'Computing checksum of file: [{path}]')
    file_hash = getattr(hashlib, algo)()
    with open(path, 'rb') as file:
        while chunk := file.read(file_hash.block_size):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def _get_child_paths(path: Path) -> List[Path]:
    if not path.is_dir():
        print(f'Could not get child paths of path because path is not a directory: [{path}]')
        return []
    try:
        return list(path.iterdir())
    except Exception as e:
        print(f'Could not read path: [{path}]. Cause: [{e}]')
        return []


def read_tree_from_disk(path: Path, compute_checksums: bool) -> Node:
    """
    Initializes a full Node tree from the contents of a path on disk.

    This will iterate through all nested elements within the input path and create Nodes representing each
    file and directory identified.

    If compute_checksums is specified as True then this will also compute the checksum of all files and attach
    said checksum to each Node representing said files.

    :param path:
    :param compute_checksums: If true this will compute the checksum of all files within the specified path.
    :return: The new Node instance initialized from the disk contents.
    """
    def attach_children(current_path: Path, current_node: Node):
        if not current_path.is_dir():
            return
        child_paths = _get_child_paths(current_path)
        if len(child_paths) == 0:
            return
        for child_path in child_paths:
            checksum = None
            if compute_checksums:
                checksum = compute_file_hash(child_path)
            child_node = Node.from_disk(current_node, child_path, checksum)
            attach_children(child_path, child_node)
    print(f'Scanning contents of: [{path}]')
    root_node = Node.from_disk(None, path, None, str(path))
    attach_children(path, root_node)
    return root_node
