from pathlib import Path
import yaml

from ..model import PathTree


def to_yaml_string(root: PathTree) -> str:
    return yaml.safe_dump(dict(root))


def to_yaml_file(output: Path | str, tree: PathTree):
    with open(output, 'w', encoding='utf-8') as file:
        file.write(to_yaml_string(tree))
