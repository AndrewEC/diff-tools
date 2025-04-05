from typing import List, Any


def has_elements(collection: List[Any]) -> bool:
    return collection is not None and len(collection) > 0
