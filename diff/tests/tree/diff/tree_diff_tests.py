import unittest

from diff.core.tree import Node
from diff.core.tree.diff import TreeDiff


class TreeDiffTests(unittest.TestCase):

    def test_diff_between_trees(self):
        # ----- first tree -----
        first_tree_root = Node(None, 'C:/parent', 0, None, None)

        first_tree_same = Node(first_tree_root, 'same', 100, 'same_checksum', None)
        first_tree_root.attach_child(first_tree_same)

        first_tree_different = Node(first_tree_root, 'different1', 100, 'same_checksum', None)
        first_tree_root.attach_child(first_tree_different)

        first_tree_similar = Node(first_tree_root, 'checksum_diff', 100, 'diff_checksum_1', None)
        first_tree_root.attach_child(first_tree_similar)

        # ----- second tree -----
        second_tree_root = Node(None, 'D:/parent', 0, None, None)

        second_tree_same = Node(second_tree_root, 'same', 100, 'same_checksum', None)
        second_tree_root.attach_child(second_tree_same)

        second_tree_different = Node(second_tree_root, 'different2', 100, 'same_checksum', None)
        second_tree_root.attach_child(second_tree_different)

        second_tree_similar = Node(second_tree_root, 'checksum_diff', 100, 'diff_checksum_2', None)
        second_tree_root.attach_child(second_tree_similar)

        # ----- comparisons -----
        actual = TreeDiff().diff_between_trees(first_tree_root, second_tree_root)

        self.assertEqual(1, len(actual.similar))
        self.assertEqual('checksum_diff', actual.similar[0][0].name)
        self.assertEqual('diff_checksum_1', actual.similar[0][0].checksum)
        self.assertEqual('checksum_diff', actual.similar[0][1].name)
        self.assertEqual('diff_checksum_2', actual.similar[0][1].checksum)

        self.assertEqual(1, len(actual.first_tree.missing))
        self.assertEqual('different2', actual.first_tree.missing[0].name)

        self.assertEqual(1, len(actual.second_tree.missing))
        self.assertEqual('different1', actual.second_tree.missing[0].name)
