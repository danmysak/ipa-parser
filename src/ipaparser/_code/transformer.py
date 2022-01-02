from itertools import chain
from typing import Iterator, Optional

from .cacher import with_cache
from .data import Combining, CombiningData, DataError, get_data, LetterData, SymbolData
from .feature_helper import extend
from .features import FeatureSet
from .matcher import Matcher
from .raw_symbol import RawSymbol

__all__ = [
    'apply_combining',
    'basic_symbol_to_features',
    'get_basic_features',
    'get_basic_matcher',
]


def apply_combining_data(data: CombiningData, combining: Combining, features: FeatureSet) -> Optional[FeatureSet]:
    transformations = data.get(combining, None)
    if transformations is None:
        return None
    result = features
    fit = False
    for feature, transformation in transformations:
        if feature in features:
            # Not "if feature in result": otherwise we would have {} -> {long} -> {extra-long} for a single 'ː'
            # as well as broken transformations of the form "C  f1  -f1, f2"
            result = transformation.apply(result)
            fit = True
    return result if fit else None


def apply_combining(combining: Combining, features: FeatureSet) -> Optional[FeatureSet]:
    return apply_combining_data(get_data().combining_recursive, combining, features)


def collect_letter_features(letters: LetterData) -> Iterator[RawSymbol]:
    for letter, features in letters.items():
        yield RawSymbol(letter, extend(features))


def collect_symbol_features(symbols: SymbolData) -> Iterator[RawSymbol]:
    for symbol, feature in symbols.items():
        yield RawSymbol(symbol, feature.extend())


def collect_basic_combined_features(combining_basic: CombiningData,
                                    non_combined: list[RawSymbol]) -> Iterator[RawSymbol]:
    for combining in combining_basic.keys():
        for symbol in non_combined:
            if (new_features := apply_combining_data(combining_basic, combining, symbol.features)) is not None:
                yield RawSymbol(combining.apply(symbol.string), new_features)


def collect_basic_features() -> dict[str, FeatureSet]:
    data = get_data()
    non_combined = list(chain(
        collect_letter_features(data.consonants),
        collect_letter_features(data.vowels),
        collect_symbol_features(data.breaks),
        collect_symbol_features(data.suprasegmentals),
    ))
    combined = list(collect_basic_combined_features(data.combining_basic, non_combined))
    feature_index: dict[str, FeatureSet] = {}
    for symbol in non_combined + combined:
        if symbol.string in feature_index:
            raise DataError(f'Symbol "{symbol.string}" can be interpreted in multiple ways')
        feature_index[symbol.string] = symbol.features
    return feature_index


get_basic_features = with_cache(collect_basic_features)


def build_basic_matcher() -> Matcher:
    return Matcher(get_basic_features().keys())


get_basic_matcher = with_cache(build_basic_matcher)


def basic_symbol_to_features(symbol: str) -> Optional[FeatureSet]:
    return get_basic_features().get(symbol, None)
