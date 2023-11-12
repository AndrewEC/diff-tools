from typing import List, Dict, Generator, Tuple

from .node import Node


class TreeResult:

    def __init__(self, tree_node: Node, missing: List[Node]):
        self.tree_node = tree_node
        self.missing = missing


class DiffResult:

    def __init__(self, similar: List[Tuple[Node, Node]], first_tree: TreeResult, second_tree: TreeResult):
        self.similar = similar
        self.first_tree = first_tree
        self.second_tree = second_tree


def _path_to_node_without_root(root_node: Node, node: Node) -> str:
    node_path = str(node.path_to_node())
    return node_path[len(root_node.name):]


def _flatten(root_node: Node) -> Dict[str, Node]:
    def flatten(node: Node) -> Generator[Tuple, None, None]:
        for child in node.children:
            yield _path_to_node_without_root(root_node, child), child
            if len(child.children) > 0:
                yield from flatten(child)

    if len(root_node.children) == 0:
        return {}
    return {value[0]: value[1] for value in flatten(root_node)}


def _are_different(first: Node, second: Node) -> bool:
    if first.checksum != '' and second.checksum != '' and first.checksum != second.checksum:
        return True
    if first.size != second.size:
        return True


def _find_similar(first_tree_nodes: Dict[str, Node], second_tree_nodes: Dict[str, Node]) -> List[Tuple[Node, Node]]:
    similarities = []
    for key in first_tree_nodes.keys():
        if key not in second_tree_nodes:
            continue
        first = first_tree_nodes[key]
        second = second_tree_nodes[key]
        if _are_different(first, second):
            similarities.append((first, second))
    return similarities


def _find_missing(first_tree_nodes: Dict[str, Node], second_tree_nodes: Dict[str, Node]) -> List[Node]:
    return [first_tree_nodes[path] for path in first_tree_nodes.keys() if path not in second_tree_nodes]


def diff_between_trees(first_tree: Node, second_tree: Node) -> DiffResult:
    """
    Identifies the diff between two different trees.

    The diff will contain the list of files that are similar between both trees (similar refers to files that
    have the same path but different sizes or checksums), files that exist in the first tree but not in the second,
    and files that exist in the second tree but not in the first.

    :param first_tree: The first tree to compare.
    :param second_tree: The second tree to compare.
    :return: The diff between both trees.
    """
    first_tree_nodes = _flatten(first_tree)
    second_tree_nodes = _flatten(second_tree)
    similar = _find_similar(first_tree_nodes, second_tree_nodes)
    nodes_not_in_second_tree = _find_missing(first_tree_nodes, second_tree_nodes)
    nodes_not_in_first_tree = _find_missing(second_tree_nodes, first_tree_nodes)
    return DiffResult(
        similar,
        TreeResult(first_tree, nodes_not_in_first_tree),
        TreeResult(second_tree, nodes_not_in_second_tree)
    )
