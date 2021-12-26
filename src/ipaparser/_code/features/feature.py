from enum import Enum
from typing import Any, TypeVar

__all__ = [
    'assert_feature_mapping',
    'Feature',
]


class Feature(str, Enum):
    pass


M = TypeVar('M', bound=dict[Feature, Any])


def assert_feature_mapping(mapping: M) -> M:
    assert mapping and set(mapping.keys()) == set(type(next(iter(mapping.keys()))))
    return mapping
