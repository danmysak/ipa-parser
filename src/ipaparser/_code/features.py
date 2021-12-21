from .definitions import features
from .definitions.features import Feature

__all__ = [
    'Feature',
    'parse_feature',
]


def build_feature_map() -> dict[str, Feature]:
    mapping: dict[str, Feature] = {}

    def append(key: str, value: Feature) -> None:
        assert key not in mapping
        mapping[key] = value

    for name in features.__all__:
        if (feature := getattr(features, name)) != Feature:
            for option in feature:
                append(option.value, option)

    return mapping


FEATURE_MAP = build_feature_map()


def parse_feature(value: str) -> Feature:
    if value not in FEATURE_MAP:
        raise ValueError(f'Unknown feature: "{value}"')
    return FEATURE_MAP[value]
