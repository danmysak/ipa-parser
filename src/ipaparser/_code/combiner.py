from dataclasses import dataclass
from itertools import chain
from typing import Iterator, Optional
import unicodedata

from .cacher import with_cache
from .data import get_data
from .data_types import Combining, CombiningType, DataError, LetterData, SymbolData
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
    transformations = (data.combining_basic if basic else data.combining_main).get(combining, [])
    for transformation in transformations:
        if transformation.is_applicable(features):
            features = transformation.apply(features)
            positive_changes = {change.feature for change in transformation.changes if change.is_positive}
            for index, meta_transformations in enumerate(data.combining_meta.get(meta_combining, [])
                                                         for meta_combining in meta or []):
                for meta_transformation in meta_transformations:
                    if meta_transformation.required == positive_changes and meta_transformation.is_applicable(features):
                        features = meta_transformation.apply(features)
                        break
                else:
                    return None
            return features
    return None


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


@dataclass
class CombiningMatchData:
    combining: Combining
    must_follow_preceding: bool
    used: bool


def match_to_features(match: Match[FeatureSet]) -> Optional[FeatureSet]:
    combining_sets = [[CombiningMatchData(combining=Combining(diacritic, CombiningType.DIACRITIC),
                                          must_follow_preceding=(index > 0 and unicodedata.combining(diacritic)
                                                                 == unicodedata.combining(diacritics[index - 1])),
                                          used=False)
                       for index, diacritic in enumerate(diacritics)]
                      for diacritics in match.extra]
    features = match.data
    while True:
        updated = False
        remaining = False
        for position in combining_sets:
            for index, combining in enumerate(position):
                if not combining.used:
                    if ((not combining.must_follow_preceding or position[index - 1].used)
                            and (next_features := apply_combining(combining.combining, features)) is not None):
                        features = next_features
                        combining.used = True
                        updated = True
                    else:
                        remaining = True
        if not remaining:
            return features
        if not updated:
            return None
