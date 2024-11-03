from typing import List, Tuple

from ..node import Node


class MissingResult:

    def __init__(self, tree_node: Node, missing: List[Node]):
        self.tree_node = tree_node
        self.missing = missing


class DiffResult:

    def __init__(self, similar: List[Tuple[Node, Node]], first_tree: MissingResult, second_tree: MissingResult):
        self.similar = similar
        self.first_tree = first_tree
        self.second_tree = second_tree
