from pathlib import Path
import os
from typing import List

from .model import PathTree


_PATH_NAMES_TO_EXCLUDE = [
    '$RECYCLE.BIN',
    'System Volume Information'
]


def _is_valid_path(path: Path) -> bool:
    return path.name not in _PATH_NAMES_TO_EXCLUDE and (path.is_file() or len(os.listdir(path)) > 0)


def _get_directory_contents(path: Path) -> List[Path]:
    return list(filter(_is_valid_path, map(path.joinpath, os.listdir(path))))


def build_path_tree(root_path: Path) -> PathTree:
    def attach_children_under_path(path_to_traverse: PathTree):
        current_path = path_to_traverse.path
        children = _get_directory_contents(current_path)
        if len(children) == 0:
            return
        path_to_traverse.set_children(children)
        for child_directory in path_to_traverse.get_child_directories():
            attach_children_under_path(child_directory)

    root = PathTree(root_path)
    attach_children_under_path(root)
    return root


def rebuild_tree_from_drive_contents(source_tree: PathTree, override: Path = None) -> PathTree:
    drive_path = source_tree.path if override is None else override
    current_tree = build_path_tree(drive_path)
    return current_tree
