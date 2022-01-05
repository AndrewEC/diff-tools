from pathlib import Path

from diff.tree import PathTree


def extract_path_to_drive_letter(path_tree: PathTree) -> Path:
    path_str = str(path_tree.path)
    index = path_str.index('\\')
    return Path(path_str[:index + 1])


def path_without_drive_letter(path: Path) -> str:
    path_str = str(path)
    index = path_str.index('\\')
    return path_str[index + 1:]
