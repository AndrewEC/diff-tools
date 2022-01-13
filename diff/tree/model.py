from __future__ import annotations
from typing import List
from pathlib import Path


class PathTree:

    def __init__(self, path: Path, size=-1, checksum=None):
        self.path = path
        self.size = path.stat().st_size if path.is_file() and size == -1 else size
        self.children: List[PathTree] = []
        self.checksum = checksum

    def add_child(self, path: Path):
        self.children.append(PathTree(path))

    def add_child_tree(self, path_tree: PathTree):
        self.children.append(path_tree)

    def set_children(self, paths: List[Path]):
        self.children = []
        for path in paths:
            self.add_child(path)

    def get_child_directories(self) -> List[PathTree]:
        return [child for child in self.children if child.path.is_dir()]

    def get_child_files(self) -> List[PathTree]:
        return [child for child in self.children if child.path.is_file()]

    def represents_directory(self) -> bool:
        return len(self.children) > 0
