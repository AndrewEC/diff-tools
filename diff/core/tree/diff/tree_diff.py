from typing import List, Dict, Generator, Tuple

from diff.core.util import has_elements

from .models import DiffResult, MissingResult
from ..node import Node


class TreeDiff:

    def diff_between_trees(self, first_tree: Node, second_tree: Node) -> DiffResult:
        """
        Identifies the diff between two different trees.

        The diff will contain the list of files that are similar between both trees (similar refers to files that
        have the same path but different sizes or checksums), files that exist in the first tree but not in the second,
        and files that exist in the second tree but not in the first.

        :param first_tree: The first tree to compare.
        :param second_tree: The second tree to compare.
        :return: The diff between both trees.
        """
        first_tree_nodes = self._flatten(first_tree)
        second_tree_nodes = self._flatten(second_tree)
        similar = self._find_similar_nodes(first_tree_nodes, second_tree_nodes)
        nodes_not_in_second_tree = self._find_missing(first_tree_nodes, second_tree_nodes)
        nodes_not_in_first_tree = self._find_missing(second_tree_nodes, first_tree_nodes)
        return DiffResult(
            similar,
            MissingResult(first_tree, nodes_not_in_first_tree),
            MissingResult(second_tree, nodes_not_in_second_tree)
        )

    def _path_to_node_without_root(self, root_node: Node, node: Node) -> str:
        node_path = str(node.path_to_node())
        return node_path[len(root_node.name):]

    def _flatten(self, root_node: Node) -> Dict[str, Node]:
        def flatten(node: Node) -> Generator[Tuple[str, Node], None, None]:
            for child in node.children:
                yield self._path_to_node_without_root(root_node, child), child
                if has_elements(child.children):
                    yield from flatten(child)

        if len(root_node.children) == 0:
            return {}
        return {value[0]: value[1] for value in flatten(root_node)}

    def _are_nodes_different(self, first: Node, second: Node) -> bool:
        if first.checksum is not None and second.checksum is not None and first.checksum != second.checksum:
            return True
        if first.size != second.size:
            return True

    def _find_similar_nodes(self, first_tree_nodes: Dict[str, Node], second_tree_nodes: Dict[str, Node]) -> List[Tuple[Node, Node]]:
        """
        Identifies all nodes between both trees that effectively have the
        same path, excluding the root, but have a different file size
        or checksum.
        """

        similarities = []
        for first_tree_node_path in first_tree_nodes.keys():
            if first_tree_node_path not in second_tree_nodes:
                continue
            first_node = first_tree_nodes[first_tree_node_path]
            second_node = second_tree_nodes[first_tree_node_path]
            if self._are_nodes_different(first_node, second_node):
                similarities.append((first_node, second_node))
        return similarities

    def _has_parent_in_missing_list(self, all_missing_nodes: List[Node], node: Node) -> bool:
        while node.parent is not None:
            if node.parent in all_missing_nodes:
                return True
            node = node.parent
        return False

    def _find_missing(self, first_tree_nodes: Dict[str, Node], second_tree_nodes: Dict[str, Node]) -> List[Node]:
        all_missing_nodes = [first_tree_nodes[path] for path in first_tree_nodes.keys() if path not in second_tree_nodes]
        # If the parent directory of a file is missing from the second tree then we should just list
        # the parent directory as missing instead of all the files within said directory.
        return [node for node in all_missing_nodes if not self._has_parent_in_missing_list(all_missing_nodes, node)]


TREE_DIFF_SINGLETON = TreeDiff()
