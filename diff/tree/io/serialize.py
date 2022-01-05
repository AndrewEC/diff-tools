from typing import Generator
from pathlib import Path

from ..model import PathTree


def to_yaml_string(root: PathTree) -> str:
    def yield_path_tree_part_as_yaml(path_tree: PathTree, depth=0) -> Generator[str, None, None]:
        yield _path_tree_to_yaml_string(path_tree, depth)
        if path_tree.path.is_dir():
            for child in path_tree.children:
                yield from yield_path_tree_part_as_yaml(child, depth + 1)

    return '\n'.join(yield_path_tree_part_as_yaml(root))


def _create_string_representation(value: PathTree, depth: int) -> str:
    def path_to_str(path: Path):
        if path.parent == path:
            return str(path)
        return str(path.name)

    indentation = '    ' * depth
    value_string = path_to_str(value.path).replace('\\', '\\\\')
    size = f';{value.size}' if value.path.is_file() else ''
    checksum = f';{value.checksum}' if value.checksum is not None else ''
    ending = ':' if value.path.is_dir() else ''
    return f'{indentation}- "{value_string}{size}{checksum}"{ending}'


def _path_tree_to_yaml_string(value: PathTree, depth: int) -> str:
    def path_to_str(path: Path):
        if path.parent == path:
            return str(path)
        return str(path.name)

    indentation = '    ' * depth
    value_string = path_to_str(value.path).replace('\\', '\\\\')

    if value.represents_directory():
        return f'{indentation}- "{value_string}":'

    yaml_string = f'{indentation}- name: {value_string}\n' \
                  f'{indentation}  size: {value.size}'
    if value.checksum is not None:
        yaml_string = f'{yaml_string}\n' \
                      f'{indentation}  checksum: {value.checksum}'
    return yaml_string

