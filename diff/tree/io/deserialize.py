from typing import Dict, Union, Hashable, Any, List
from pathlib import Path

import yaml

from ..model import PathTree


def from_yaml_string(yaml_string: str) -> PathTree:
    parsed = yaml.safe_load(yaml_string)
    first_available_key = next((_ for _ in parsed[0].keys()))
    root = PathTree(Path(first_available_key))
    _append_child_paths_from_element(parsed[0][first_available_key], root)
    return root


def _append_child_paths_from_element(yaml_element: Union[Dict[Hashable, Any], List],
                                     path_tree: PathTree):

    if type(yaml_element) is list:
        _append_child_elements_from_list(yaml_element, path_tree)
    elif type(yaml_element) is dict:
        _append_child_elements_from_dictionary(yaml_element, path_tree)


def _append_child_elements_from_dictionary(yaml_element: Dict[Hashable, Any],
                                           path_tree: PathTree):

    for key in yaml_element.keys():
        child_tree = PathTree(path_tree.path.joinpath(key))
        path_tree.add_child_tree(child_tree)
        _append_child_paths_from_element(yaml_element[key], child_tree)


def _parse_path_tree_from_element(yaml_element: Dict[Hashable, str], path_tree: PathTree) -> PathTree:
    size = int(yaml_element['size'])
    checksum = yaml_element['checksum'] if 'checksum' in yaml_element else None
    path = path_tree.path.joinpath(yaml_element['name'])
    return PathTree(path, size, checksum)


def _append_child_elements_from_list(yaml_element: List,
                                     path_tree: PathTree):

    for element in yaml_element:
        if type(element) is dict:
            if 'name' in element:
                child_tree = _parse_path_tree_from_element(element, path_tree)
                path_tree.add_child_tree(child_tree)
            else:
                _append_child_paths_from_element(element, path_tree)
        elif type(element) is list:
            _append_child_paths_from_element(element, path_tree)
