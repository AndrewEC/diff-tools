import yaml

from ..model import PathTree


def to_yaml_string(root: PathTree) -> str:
    return yaml.safe_dump(dict(root))

