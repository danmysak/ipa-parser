from functools import partial
from typing import Optional, TypeVar

from .features import Feature, FEATURE_KINDS, FeatureKind, FeatureSet

__all__ = [
    'equivalent',
    'exclude',
    'extend',
    'include',
    'find_feature',
    'find_feature_kind',
]

T = TypeVar('T')

FeatureMap = dict[str, Feature]
KindMap = dict[str, FeatureKind]


def append_unique(mapping: dict[str, T], key: str, value: T) -> None:
    assert key not in mapping
    mapping[key] = value


def build_maps() -> tuple[FeatureMap, KindMap]:
    feature_map: FeatureMap = {}
    kind_map: KindMap = {}

    for kind in FEATURE_KINDS:
        for feature in kind:
            feature: Feature
            append_unique(feature_map, feature.value, feature)
        for kind_name in kind.kind_values():
            append_unique(kind_map, kind_name, kind)

    return feature_map, kind_map


FEATURE_MAP, KIND_MAP = build_maps()


def find_feature(value: str) -> Optional[Feature]:
    return FEATURE_MAP.get(value, None)


def find_feature_kind(value: str) -> Optional[FeatureKind]:
    return KIND_MAP.get(value, None)


def extend(feature_set: FeatureSet) -> FeatureSet:
    return frozenset().union(*(feature.extend() for feature in feature_set))


def include(kinds: set[FeatureKind], feature_set: FeatureSet) -> FeatureSet:
    return frozenset(feature for feature in feature_set if any(isinstance(feature, kind) for kind in kinds))


def exclude(kinds: set[FeatureKind], feature_set: FeatureSet) -> FeatureSet:
    return feature_set - extend(include(kinds, feature_set))


def equivalent(a: FeatureSet, b: FeatureSet, included: Optional[set[FeatureKind]] = None,
               *, excluded: Optional[set[FeatureKind]] = None) -> bool:
    for processor, kinds in ((include, included),
                             (exclude, excluded)):
        if kinds is not None:
            a, b = map(partial(processor, kinds), (a, b))
    return a == b
