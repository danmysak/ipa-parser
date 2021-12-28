from enum import Enum
from typing import Any, TypeVar

__all__ = [
    'assert_feature_mapping',
    'Feature',
    'FeatureSet',
]


class Feature(str, Enum):
    """The base class for all features; compatible with strings."""
    pass


FeatureSet = frozenset[Feature]


M = TypeVar('M', bound=dict[Feature, Any])


def assert_feature_mapping(mapping: M) -> M:
    assert mapping and set(mapping.keys()) == set(type(next(iter(mapping.keys()))))
    return mapping
