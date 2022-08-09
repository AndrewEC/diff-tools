from .model import PathTree


def count_child_directories(tree: PathTree) -> int:
    child_directories = tree.get_child_directories()
    tally = len(child_directories)
    for directory in child_directories:
        tally = tally + count_child_directories(directory)
    return tally


def count_child_files(tree: PathTree) -> int:
    tally = 0
    for child in tree.children:
        if child.path.is_dir():
            tally = tally + count_child_files(child)
        else:
            tally = tally + 1
    return tally
