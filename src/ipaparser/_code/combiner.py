from dataclasses import dataclass
from itertools import chain
from typing import Iterable, Iterator, Optional

from .cacher import with_cache
from .data import get_data
from .data_types import ChangeSequence, Combining, CombiningType, DataError, LetterData, SymbolData, Transformation
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


@dataclass(frozen=True)
class AppliedCombiningData:
    features: FeatureSet
    transformations: list[Transformation]


def apply_combining(
        combining: Combining,
        features: FeatureSet,
        *,
        basic: bool = False,
        meta: Optional[list[Combining]] = None,
        allowed: Optional[set[ChangeSequence]] = None,
        disallowed: Optional[set[ChangeSequence]] = None,
) -> Optional[AppliedCombiningData]:
    data = get_data()
    transformations = (data.combining_basic if basic else data.combining_main).get(combining, [])
    for transformation in transformations:
        if (transformation.changes not in (disallowed or set())
                and (transformation.changes in (allowed or set()) or transformation.is_applicable(features))):
            applied_transformations: list[Transformation] = []

            def apply(current_transformation: transformation) -> None:
                nonlocal features
                features = current_transformation.apply(features)
                applied_transformations.append(current_transformation)

            apply(transformation)
            positive_changes = {change.feature for change in transformation.changes if change.is_positive}
            for index, meta_transformations in enumerate(data.combining_meta.get(meta_combining, [])
                                                         for meta_combining in meta or []):
                for meta_transformation in meta_transformations:
                    if meta_transformation.required == positive_changes and meta_transformation.is_applicable(features):
                        apply(meta_transformation)
                        break
                else:
                    return None
            return AppliedCombiningData(features, applied_transformations)
    return None


def wrap_diacritics(diacritics: Iterable[str]) -> list[Combining]:
    return [Combining(diacritic, CombiningType.DIACRITIC) for diacritic in diacritics]


def apply_position(position: StringPosition, features: FeatureSet, *, is_preceding: bool) -> Optional[FeatureSet]:
    main, diacritics = position[0], position[1:]
    applied = apply_combining(
        combining=Combining(
            character=main,
            type=CombiningType.PRECEDING if is_preceding else CombiningType.FOLLOWING,
        ),
        features=features,
        meta=wrap_diacritics(diacritics),
    )
    return applied.features if applied else None


def collect_letter_features(letters: LetterData) -> Iterator[RawSymbol]:
    for letter, features in letters.items():
        yield RawSymbol(letter, extend(features))


def collect_symbol_features(symbols: SymbolData) -> Iterator[RawSymbol]:
    for symbol, feature in symbols.items():
        yield RawSymbol(symbol, feature.extend())


def collect_basic_combined_features(non_combined: list[RawSymbol]) -> Iterator[RawSymbol]:
    for combining in get_data().combining_basic.keys():
        for symbol in non_combined:
            if applied := apply_combining(combining, symbol.features, basic=True):
                yield RawSymbol(combining.apply(symbol.string), applied.features)


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


def apply_match_position(diacritics: list[Combining], history: set[ChangeSequence],
                         features: FeatureSet) -> Optional[tuple[FeatureSet, set[ChangeSequence]]]:
    changes: set[ChangeSequence] = set()
    while True:
        remaining: list[Combining] = []
        for combining in diacritics:
            if applied := apply_combining(
                    combining,
                    features,
                    allowed=history - changes,
                    disallowed=set(tuple(change.negate() for change in sequence) for sequence in history | changes),
            ):
                features = applied.features
                changes.update(transformation.changes for transformation in applied.transformations)
            else:
                remaining.append(combining)
        if not remaining:
            return features, changes
        if len(remaining) == len(diacritics):
            return None
        diacritics = remaining


def match_to_features(match: Match[FeatureSet]) -> Optional[FeatureSet]:
    features = match.data
    history: set[ChangeSequence] = set()
    for position in match.extra:
        if applied := apply_match_position(wrap_diacritics(position), history, features):
            features, changes = applied
            history.update(changes)
        else:
            return None
    return features
