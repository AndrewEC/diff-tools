from __future__ import annotations
from typing import List, Dict
from pathlib import Path
import os


_MESSAGE_TEMPLATE = 'Could not read Node. "{}" is missing.'
_REQUIRED_KEYS = ['name', 'size', 'checksum', 'children']


def _find_missing_key(value: Dict) -> str | None:
    return next((key for key in _REQUIRED_KEYS if key not in value), None)


def _validate_node_dict(value: Dict):
    missing_key = _find_missing_key(value)
    if missing_key is None:
        return
    raise ValueError(_MESSAGE_TEMPLATE.format(missing_key))



class Node:

    """
    Represents a single file or directory.
    """

    def __init__(self, parent: Node | None, name: str, size: int, checksum: str | None):
        self.parent = parent
        self.name = name
        self.size = size
        self.checksum = checksum if checksum is not None else ''
        self.children: List[Node] = []

    def attach_child(self, node: Node):
        """
        Adds a single node to the list of child nodes this node currently has.

        :param node: The node to be appended to the current list of child nodes.
        """
        self.children.append(node)

    def path_to_node(self) -> Path:
        """
        The absolute path to the current node. This will combine the names of all the parent
        nodes of this node then join them together to form the complete path.

        :return: The absolute path to the current node.
        """
        path_segments = [self.name]
        current_parent = self.parent
        while current_parent is not None:
            path_segments.append(current_parent.name)
            current_parent = current_parent.parent
        return Path(os.path.join(*list(reversed(path_segments))))

    def to_dict(self) -> Dict:
        """
        Serializes this Node to a dictionary.

        :return: A dictionary representation of this Node.
        """
        return {
            'name': self.name,
            'size': self.size,
            'checksum': self.checksum,
            'children': [child.to_dict() for child in self.children]
        }

    @staticmethod
    def from_disk(parent: Node | None, path: Path, checksum: str | None, alternate_name: str | None = None) -> Node:
        """
        Initializes a Node instance from a Path that currently exists on disk.

        :param parent: The parent Node the newly created Node will be a child of. If this value is not None then
            the attach_child function of the parent Node will be invoked.
        :param path: The existing, on disk, path that the newly created Node will represent.
        :param checksum: An optional checksum of the file on disk. This should be None if the path points to a
            directory.
        :param alternate_name: By default, the name of the new node is equal to path.name. If this value is not None
            it will override said default value.
        :return:
        """
        if path.is_dir() and (checksum is not None and checksum != ''):
            raise ValueError('Could not initialize Node from disk. The checksum value must be None or empty if the path points to a directory.')
        size = os.stat(path).st_size if path.is_file() else -1
        name = path.name if alternate_name is None else alternate_name
        node = Node(parent, name, size, checksum)
        if parent is not None:
            parent.attach_child(node)
        return node

    @staticmethod
    def from_dict(parent: Node | None, values: Dict) -> Node:
        """
        Initializes a Node instance from the values in a dictionary.

        :param parent: The parent Node the newly created node will be a child of. If this value is not None then
            the attach_child function of the parent Node will be invoked.
        :param values: The dictionary containing the values to initialize the new Node.
        :return: A newly initialized Node with the constructor values pulled from the values dict.
        """
        _validate_node_dict(values)
        node = Node(parent, values['name'], int(values['size']), values['checksum'])
        if parent is not None:
            parent.attach_child(node)
        children = values['children']
        if len(children) > 0:
            for child in children:
                Node.from_dict(node, child)
        return node
