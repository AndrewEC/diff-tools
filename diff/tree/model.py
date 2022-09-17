from __future__ import annotations
from typing import List
from pathlib import Path


class PathTree:

    def __init__(self, path: Path, size=-1, checksum=None, parent: PathTree = None):
        self.path = path
        self.size = path.stat().st_size if path.is_file() and size == -1 else size
        self.children: List[PathTree] = []
        self.checksum = checksum
        self.parent = parent

    def add_child(self, path: Path):
        self.children.append(PathTree(path, parent=self))

    def create_and_append_child_tree(self, path: Path, size=-1, checksum=None) -> PathTree:
        path_tree = PathTree(path, size, checksum, self)
        self.children.append(path_tree)
        return path_tree

    def set_children(self, paths: List[Path]):
        self.children = []
        for path in paths:
            self.add_child(path)

    def get_child_directories(self) -> List[PathTree]:
        return [child for child in self.children if child.path.is_dir()]

    def get_child_files(self) -> List[PathTree]:
        return [child for child in self.children if not child.represents_directory()]

    def represents_directory(self) -> bool:
        return len(self.children) > 0

    def get_root(self):
        value = self
        while value.parent is not None:
            value = value.parent
        return value

    def __iter__(self):
        def root_name(path: Path):
            if self.parent is None:
                return str(path)
            return str(path.name)

        if self.represents_directory():
            yield root_name(self.path), list(map(dict, self.children))
        else:
            yield 'name', self.path.name
            yield 'size', self.size
            if self.checksum is not None:
                yield 'checksum', self.checksum
