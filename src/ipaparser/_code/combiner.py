from dataclasses import dataclass
from functools import partial
from typing import Iterable, Optional, TypeVar

from .cacher import with_cache
from .data import get_data
from .data_types import ChangeSequence, Combining, CombiningType, DataError, Symbol, Transformation
from .feature_helper import extend
from .features import FeatureSet
from .matcher import Match, Matcher, MatchOption
from .strings import StringPosition, to_positions

__all__ = [
    'apply_position',
    'get_matcher',
    'match_to_feature_sets',
]

T = TypeVar('T')


def not_none(values: Iterable[Optional[T]]) -> list[T]:
    return [value for value in values if value is not None]


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
                                                         for meta_combining in (meta or [])):
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


def apply_position_single(position: StringPosition, features: FeatureSet,
                          *, is_preceding: bool) -> Optional[FeatureSet]:
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


def apply_position(position: StringPosition, feature_sets: list[FeatureSet], *, is_preceding: bool) -> list[FeatureSet]:
    return not_none(map(partial(apply_position_single, position, is_preceding=is_preceding), feature_sets))


def extend_symbol(symbol: Symbol) -> Symbol:
    return Symbol(
        string=symbol.string,
        is_main_interpretation=symbol.is_main_interpretation,
        features=extend(symbol.features),
    )


def collect_basic_combined_symbols(extended_non_combined: set[Symbol]) -> set[Symbol]:
    return {
        Symbol(
            string=combining.apply(symbol.string),
            is_main_interpretation=symbol.is_main_interpretation,
            features=applied.features,
        )
        for combining in get_data().combining_basic.keys()
        for symbol in extended_non_combined
        if (applied := apply_combining(combining, symbol.features, basic=True))
    }


def check_basic_symbol_uniqueness(symbols: set[Symbol]) -> set[Symbol]:
    encountered: set[str] = set()
    for symbol in symbols:
        if symbol.is_main_interpretation:
            if symbol.string in encountered:
                raise DataError(f'"{symbol.string}" can be interpreted in multiple ways')
            encountered.add(symbol.string)
    return symbols


def collect_basic_symbols() -> set[Symbol]:
    data = get_data()
    non_combined = set(map(
        extend_symbol,
        data.consonants | data.vowels | data.breaks | data.suprasegmentals,
    ))
    return check_basic_symbol_uniqueness(non_combined | collect_basic_combined_symbols(non_combined))


def build_matcher() -> Matcher[Symbol]:
    def option_key(option: MatchOption[Symbol]) -> tuple[int, ...]:
        return (
            0 if option.data.is_main_interpretation else 1,
            -len(option.data.string),
        )

    return Matcher([(to_positions(symbol.string), symbol) for symbol in collect_basic_symbols()], option_key)


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


def match_option_to_features(match: MatchOption[Symbol]) -> Optional[FeatureSet]:
    features = match.data.features
    history: set[ChangeSequence] = set()
    for position in match.combining:
        if applied := apply_match_position(wrap_diacritics(position), history, features):
            features, changes = applied
            history.update(changes)
        else:
            return None
    return features


def match_to_feature_sets(match: Match[Symbol]) -> list[FeatureSet]:
    return not_none(map(match_option_to_features, match.options))
