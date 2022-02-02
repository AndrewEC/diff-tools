from diff.tree import PathTree, get_root


def path_without_root(path_tree: PathTree) -> str:
    root = get_root(path_tree)
    return str(path_tree.path).replace(str(root.path), '')
