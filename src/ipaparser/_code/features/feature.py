from __future__ import annotations
from enum import Enum
from typing import Any, final, Optional, TypeVar

__all__ = [
    'assert_feature_mapping',
    'Feature',
    'FeatureSet',
]


class Feature(str, Enum):
    """The base class for all features; compatible with strings."""

    def derived(self) -> Optional[Feature]:
        """Return the most specific derived feature of the caller, if any."""
        assert self  # Avoiding "should be a static method" warning
        return None

    @final
    def extend(self) -> FeatureSet:
        """Return a (frozen)set containing the derived features of the caller and the caller itself."""
        feature = self
        features: set[Feature] = {feature}
        while feature := feature.derived():
            features.add(feature)
        return frozenset(features)


FeatureSet = frozenset[Feature]

M = TypeVar('M', bound=dict[Feature, Any])


def assert_feature_mapping(mapping: M) -> M:
    assert mapping and set(mapping.keys()) == set(type(next(iter(mapping.keys()))))
    return mapping
