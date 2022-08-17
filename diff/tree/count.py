from .model import PathTree


def count_child_directories(tree: PathTree) -> int:
    """
    Count the total number of directory children of the PathTree.

    :param tree: The tree to count the number child directories.
    :return: A count of the number of child directories.
    """
    child_directories = tree.get_child_directories()
    tally = len(child_directories)
    for directory in child_directories:
        tally = tally + count_child_directories(directory)
    return tally


def count_child_files(tree: PathTree) -> int:
    """
    Count the total number of file children of the PathTree.

    :param tree: The tree to count the number of child files.
    :return: A count of the number of child files.
    """
    tally = 0
    for child in tree.children:
        if child.path.is_dir():
            tally = tally + count_child_files(child)
        else:
            tally = tally + 1
    return tally
