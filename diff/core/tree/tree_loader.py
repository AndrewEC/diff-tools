from typing import List, Dict, Any, Final
import os
from pathlib import Path

from diff.core.errors import InvalidScanFileException
from diff.core.util import Checksum, CHECKSUM_SINGLETON

from .node import Node
from .yml import YamlSerialization, YAML_SERIALIZATION_SINGLETON


DEFAULT_HASH_ALGORITHM: Final[str] = 'sha256'

AVAILABLE_HASH_ALGORITHMS: Final[List[str]] = [
    DEFAULT_HASH_ALGORITHM,
    'sha512'
]

_SKIPPABLE_FILES: Final[List[str]] = [
]

_SKIPPABLE_FOLDERS: Final[List[str]] = [
    'System Volume Information',
    '$RECYCLE.BIN'
]


class TreeLoader:

    def __init__(self,
                 yaml_serialization: YamlSerialization = YAML_SERIALIZATION_SINGLETON,
                 checksum: Checksum = CHECKSUM_SINGLETON):
        self._yaml_serialization = yaml_serialization
        self._checksum = checksum

    def read_tree_from_yaml(self, file_path: Path) -> Node:
        """
        Parses a yaml file to a dict and reads the dict into a Node instance that represents the root of the
        tree with all children attached.

        :param file_path: The path to the yaml file to read.
        :return: A Node instance deserialized from the yaml file content.
        """
        print(f'Reading contents of scan file: [{file_path}]')
        try:
            return Node.from_dict(None, self._yaml_serialization.read_yaml_file(file_path))
        except Exception as e:
            raise InvalidScanFileException(file_path, e) from e

    def read_tree_from_disk(self, path: Path, compute_checksums: bool, checksum_algo: str | None) -> Node:
        """
        Initializes a full Node tree from the contents of a path on disk.

        This will iterate through all nested elements within the input path and create Nodes representing each
        file and directory identified.

        If compute_checksums is specified as True then this will also compute the checksum of all files and attach
        said checksum to each Node representing said files.

        :param path: The path to the directory whose contents are to be scanned by this function.
        :param compute_checksums: If true this will compute the checksum of all files within the specified path.
        :param checksum_algo: The algorithm to use to compute the checksum of the files on disk.
        :return: The new Node instance initialized from the disk contents.
        """
        def attach_children(current_path: Path, current_node: Node):
            if not current_path.is_dir():
                return
            child_paths = self._get_non_skippable_files(current_path)
            if len(child_paths) == 0:
                return
            for child_path in child_paths:
                child_node = self._read_node_details(child_path, current_node, compute_checksums, checksum_algo, None)
                attach_children(child_path, child_node)

        print(f'Scanning contents of: [{path}]')
        root_node = self._read_node_details(path, None, False, checksum_algo, str(path))
        attach_children(path, root_node)
        return root_node

    def _read_node_details(self,
                           path: Path,
                           parent: Node | None,
                           compute_checksum: bool,
                           checksum_algo: str | None,
                           alternate_name: str | None) -> Node:

        values: Dict[str, Any] = {
            'name': path.name,
            'size': os.stat(path).st_size if path.is_file() else None,
        }

        if alternate_name is not None:
            values['alternate_name'] = alternate_name

        if compute_checksum and checksum_algo is not None and path.is_file():
            values['checksum'] = self._checksum.compute_file_checksum(path, checksum_algo)

        if parent is None:
            values['checksum_algo'] = checksum_algo

        return Node.from_dict(parent, values)

    def _should_skip_file(self, path: Path) -> bool:
        return (
                (path.is_dir() and path.name in _SKIPPABLE_FOLDERS)
                or (path.is_file() and path.name in _SKIPPABLE_FILES)
        )

    def _get_non_skippable_files(self, path: Path) -> List[Path]:
        all_files = path.iterdir()
        non_skippable_files: List[Path] = []
        for file in all_files:
            if self._should_skip_file(file):
                print(f'Skipping file since it has an excluded name: [{file.name}]')
            else:
                non_skippable_files.append(file)
        return non_skippable_files


TREE_LOADER_SINGLETON: Final[TreeLoader] = TreeLoader()
