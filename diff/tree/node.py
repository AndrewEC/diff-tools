from __future__ import annotations
from typing import List, Dict
from pathlib import Path
import os

from diff.errors import InvalidNodePropertiesException


_MESSAGE_TEMPLATE = 'Could not read Node. Found an unrecognized property of "{}".'
_VALID_NODE_KEYS = ['name', 'size', 'checksum', 'checksum_algo', 'children']


def _validate_properties(value: Dict):
    unrecognized_key = next((key for key in value if key not in _VALID_NODE_KEYS), None)
    if unrecognized_key is not None:
        raise InvalidNodePropertiesException(unrecognized_key)


def _get_size(value: Dict) -> int | None:
    size = value.get('size')
    return int(size) if size is not None else None


class Node:

    """
    Represents a single file or directory.
    """

    def __init__(
            self,
            parent: Node | None,
            name: str,
            size: int,
            checksum: str | None,
            checksum_algo: str | None
    ):
        self.parent = parent
        self.name = name
        self.size = size
        self.checksum = checksum
        self.children: List[Node] | None = None
        self.checksum_algo = checksum_algo

    def attach_child(self, node: Node):
        """
        Adds a single node to the list of child nodes this node currently has.

        :param node: The node to be appended to the current list of child nodes.
        """
        if self.children is None:
            self.children = []
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
        if len(path_segments) == 1:
            return Path(path_segments[0])
        return Path(os.path.join(*list(reversed(path_segments))))

    def to_dict(self) -> Dict:
        """
        Serializes this Node to a dictionary.

        :return: A dictionary representation of this Node.
        """
        node_dict = {
            'name': self.name
        }

        if self.size is not None:
            node_dict['size'] = self.size

        if self.children is not None and len(self.children) > 0:
            node_dict['children'] = [child.to_dict() for child in self.children]

        if self.checksum is not None:
            node_dict['checksum'] = self.checksum

        if self.checksum_algo is not None:
            node_dict['checksum_algo'] = self.checksum_algo

        return node_dict

    @staticmethod
    def from_disk(
            parent: Node | None,
            path: Path,
            checksum: str | None,
            checksum_algo: str | None,
            alternate_name: str | None = None
    ) -> Node:
        """
        Initializes a Node instance from a Path that currently exists on disk.

        :param parent: The parent Node the newly created Node will be a child of. If this value is not None then
            the attach_child function of the parent Node will be invoked.
        :param path: The existing, on disk, path that the newly created Node will represent.
        :param checksum: An optional checksum of the file on disk. This value must be None if the path parameter
            points to a directory.
        :param checksum_algo: The algorithm used to calculate the checksum of the file. This value must be provided if
            the checksum value is also provided
        :param alternate_name: By default, the name of the new node is equal to path.name. If this value is not None
            it will override said default value.
        :return:
        """
        if path.is_dir() and checksum is not None:
            raise ValueError('Could not initialize Node from disk. The checksum value must be None or empty if the path points to a directory.')
        size = os.stat(path).st_size if path.is_file() else None
        name = path.name if alternate_name is None else alternate_name
        node = Node(parent, name, size, checksum, checksum_algo)
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
        _validate_properties(values)
        node = Node(parent, values['name'], _get_size(values), values.get('checksum'), values.get('checksum_algo'))
        if parent is not None:
            parent.attach_child(node)
        children = values.get('children')
        if children is not None and len(children) > 0:
            for child in children:
                Node.from_dict(node, child)
        return node
