from __future__ import annotations
from enum import Enum
from typing import Any, final, Optional, Type, TypeVar

__all__ = [
    'assert_feature_mapping',
    'Feature',
    'FeatureKind',
    'FeatureSet',
]


def upper_camel_to_spaces(string: str) -> str:
    result: list[str] = []
    for index, character in enumerate(string):
        if character.isupper():
            if index > 0:
                result.append(' ')
            result.append(character.lower())
        else:
            result.append(character)
    return ''.join(result)


class Feature(str, Enum):
    """The base class for all features; compatible with strings."""

    @classmethod
    @final
    def kind_values(cls) -> tuple[str, ...]:
        """Return supported string representations for the kind of features."""
        return (cls.__name__, upper_camel_to_spaces(cls.__name__)) if cls != Feature else ()

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
FeatureKind = Type[Feature]

M = TypeVar('M', bound=dict[Feature, Any])


def assert_feature_mapping(mapping: M) -> M:
    assert mapping and set(mapping.keys()) == set(type(next(iter(mapping.keys()))))
    return mapping
