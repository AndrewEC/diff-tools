from typing import Dict
from pathlib import Path
import yaml

from .node import Node


class YamlSerialization:

    def to_yaml_string(self, root_node: Node) -> str:
        """
        Serializes the input Node instance to yaml.

        :param root_node: The node to be serialized to yaml.
        :return: A formatted yaml string ready to be written to a file.
        """
        return yaml.safe_dump(root_node.to_dict())

    def to_yaml_file(self, file_path: Path, root_node: Node):
        """
        Serializes the input Node instance to yaml and writes the yaml content to file.

        :param file_path: The path to the yaml file to create/write to.
        :param root_node: The Node to be serialized to yaml.
        """
        with open(file_path, 'w') as file:
            file.write(self.to_yaml_string(root_node))

    def read_yaml_file(self, file_path: Path) -> Dict:
        """
        Reads the contents of a yaml file to a dictionary.

        :param file_path: The path to the Yaml file.
        :return: The deserialized dictionary contents of the file.
        """
        with open(file_path, 'r') as file:
            return yaml.safe_load(file.read())


YAML_SERIALIZATION_SINGLETON = YamlSerialization()
