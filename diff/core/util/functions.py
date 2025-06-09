from typing import List, Any, TypeVar


T = TypeVar('T')


def has_elements(collection: List[Any] | None) -> bool:
    return collection is not None and len(collection) > 0


def either(value: T | None, default: T) -> T:
    return value if value is not None else default
