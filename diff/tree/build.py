from pathlib import Path
import os
from typing import List

from .model import PathTree


def _is_valid_path(path: Path) -> bool:
    return path.is_file() or len(os.listdir(path)) > 0


def _get_directory_contents(path: Path) -> List[Path]:
    return list(filter(_is_valid_path, map(path.joinpath, os.listdir(path))))


def build_path_tree(root_path: Path) -> PathTree:
    """
    Scans the specified path to identify all files, directories, and their locations and builds out a PathTree
    instance containing a trie like structure of all said directories, files, and their locations.

    This will log a message but otherwise skip files and directories that cannot be read. For example if one of the
    child directories of the root path requires read permissions the user does not have this method will skip that
    directory and its children but won't throw an exception.

    :param root_path: The path to start the scan from. This needs to be a directory to have any real effect.
    :return: A PathTree instance containing a trie like structure mapping all child files and directories of the
    input root path.
    """
    def try_attach_children_under_path(path_to_traverse: PathTree):
        try:
            current_path = path_to_traverse.path
            children = _get_directory_contents(current_path)
            if len(children) == 0:
                return
            path_to_traverse.set_children(children)
            for child_directory in path_to_traverse.get_child_directories():
                try_attach_children_under_path(child_directory)
        except Exception as e:
            print(f'Could not scan directory: [{path_to_traverse}]. Cause: [{e}]')

    root = PathTree(root_path)
    try_attach_children_under_path(root)
    return root


def rebuild_tree_from_folder_contents(source_tree: PathTree, override: Path = None) -> PathTree:
    """
    Extracts the root path from the input PathTree and scans the current file system to create a new PathTree instance
    with the same root as the source tree but with the updated file information.

    :param source_tree: The input source tree from which the root scan path will be parsed from.
    :param override: If provided this path will be used in place of the root path of the source tree when
    initiating the scan.
    :return: A new PathTree instance with a root matching the source tree root or, if provided, the path specified
    in the override parameter.
    """
    root_path = source_tree.path if override is None else override
    return build_path_tree(root_path)
