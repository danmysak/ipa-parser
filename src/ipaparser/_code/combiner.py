from itertools import chain
from typing import Iterator, Optional

from .cacher import with_cache
from .data import get_data
from .data_types import Combining, CombiningType, DataError, LetterData, SymbolData, Transformation
from .feature_helper import extend
from .features import FeatureSet
from .matcher import Match, Matcher
from .raw_symbol import RawSymbol
from .strings import StringPosition, StringPositions, to_positions

__all__ = [
    'apply_position',
    'get_matcher',
    'match_to_features',
]


def apply_combining(combining: Combining, features: FeatureSet,
                    *, basic: bool = False, meta: Optional[list[Combining]] = None) -> Optional[FeatureSet]:
    data = get_data()
    transformations = (data.combining_basic if basic else data.combining_recursive).get(combining, [])
    applicable: list[Transformation] = []
    # Transformations should not be applied as we go: otherwise we would have {} -> {long} -> {extra-long} for
    # a single 'ː' as well as broken transformations of the form "C  f1  -f1, f2"
    meta_transformation_sets = [data.combining_meta.get(meta_combining, []) for meta_combining in meta or []]
    meta_used_by_index = [False for _ in meta_transformation_sets]
    for transformation in transformations:
        if transformation.is_applicable(features):
            applicable.append(transformation)
            if transformation.change and transformation.change.is_positive:
                for index, meta_transformations in enumerate(meta_transformation_sets):
                    for meta_transformation in meta_transformations:
                        if meta_transformation.required == transformation.change.feature:
                            applicable.append(meta_transformation)
                            meta_used_by_index[index] = True
    if applicable and all(meta_used_by_index):
        for transformation in applicable:
            features = transformation.apply(features)
        return features
    else:
        return None


def apply_combining_sequence(sequence: list[Combining], features: FeatureSet) -> Optional[FeatureSet]:
    for combining in sequence:
        if (features := apply_combining(combining, features)) is None:
            break
    return features


def apply_position(position: StringPosition, features: FeatureSet, *, is_preceding: bool) -> Optional[FeatureSet]:
    main, diacritics = position[0], position[1:]
    return apply_combining(
        combining=Combining(
            character=main,
            type=CombiningType.PRECEDING if is_preceding else CombiningType.FOLLOWING,
        ),
        features=features,
        meta=[Combining(diacritic, CombiningType.DIACRITIC) for diacritic in diacritics],
    )


def collect_letter_features(letters: LetterData) -> Iterator[RawSymbol]:
    for letter, features in letters.items():
        yield RawSymbol(letter, extend(features))


def collect_symbol_features(symbols: SymbolData) -> Iterator[RawSymbol]:
    for symbol, feature in symbols.items():
        yield RawSymbol(symbol, feature.extend())


def collect_basic_combined_features(non_combined: list[RawSymbol]) -> Iterator[RawSymbol]:
    for combining in get_data().combining_basic.keys():
        for symbol in non_combined:
            if (new_features := apply_combining(combining, symbol.features, basic=True)) is not None:
                yield RawSymbol(combining.apply(symbol.string), new_features)


def collect_basic_features() -> dict[StringPositions, FeatureSet]:
    data = get_data()
    non_combined = list(chain(
        collect_letter_features(data.consonants),
        collect_letter_features(data.vowels),
        collect_symbol_features(data.breaks),
        collect_symbol_features(data.suprasegmentals),
    ))
    combined = list(collect_basic_combined_features(non_combined))
    feature_index: dict[StringPositions, FeatureSet] = {}
    for symbol in non_combined + combined:
        key = to_positions(symbol.string)
        if key in feature_index:
            raise DataError(f'Symbol "{symbol.string}" can be interpreted in multiple ways')
        feature_index[key] = symbol.features
    return feature_index


def build_matcher() -> Matcher[FeatureSet]:
    return Matcher(collect_basic_features())


get_matcher = with_cache(build_matcher)


def match_to_features(match: Match[FeatureSet]) -> Optional[FeatureSet]:
    return apply_combining_sequence(
        sequence=[Combining(diacritic, CombiningType.DIACRITIC) for diacritic in sorted(set(match.extra))],
        features=match.data,
    )
