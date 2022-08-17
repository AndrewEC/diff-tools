from pathlib import Path
import yaml

from ..model import PathTree


def to_yaml_string(root: PathTree) -> str:
    """
    Serializes the PathTree instance to a valid yaml string.
    :param root: The PathTree to serialize to yaml.
    :return: A yaml string representation of the PathTree.
    """
    return yaml.safe_dump(dict(root))


def to_yaml_file(output: Path | str, tree: PathTree):
    """
    Serializes the PathTree instance to yaml and writes the yaml string to the specified output file.
    :param output: The path or str representing the location of where the yaml file will be written to.
    :param tree: The PathTree to be serialized to yaml and writtent to the output file.
    """
    with open(output, 'w', encoding='utf-8') as file:
        file.write(to_yaml_string(tree))
