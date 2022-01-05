from .model import PathTree


def count_child_directories(tree: PathTree) -> int:
    def count(path_tree: PathTree) -> int:
        child_directories = path_tree.get_child_directories()
        tally = len(child_directories)
        for directory in child_directories:
            tally = tally + count(directory)
        return tally

    return count(tree)


def count_child_files(tree: PathTree) -> int:
    def count(path_tree: PathTree) -> int:
        tally = 0
        for child in path_tree.children:
            if child.path.is_dir():
                tally = tally + count(child)
            else:
                tally = tally + 1
        return tally

    return count(tree)
