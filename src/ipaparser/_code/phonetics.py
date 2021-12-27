from itertools import chain
from typing import Callable, Iterator, Optional, Type, TypeVar

from .cacher import with_cache
from .data import Combining, CombiningData, DataError, get_data, LetterData, SymbolData
from .features import (
    Airflow,
    Backness,
    Feature,
    Height,
    Intonation,
    Manner,
    Place,
    SoundSubtype,
    StressSubtype,
    SuprasegmentalType,
    Syllabicity,
    SymbolType,
    Tone,
    ToneNumber,
    ToneStep,
    ToneType,
)
from .matcher import Matcher

__all__ = [
    'apply_combining',
    'basic_symbol_to_features',
    'combine_features',
    'get_basic_features',
    'get_basic_matcher',
    'unknown',
]

FeatureExtender = Callable[[set[Feature]], set[Feature]]
SymbolWithFeatures = tuple[str, set[Feature]]

F = TypeVar('F', bound=Feature)


def get_extender(feature_class: Type[F], extender: Callable[[F], set[Feature]]) -> FeatureExtender:
    return lambda features: features.union(*(extender(feature) for feature in features
                                             if isinstance(feature, feature_class)))


extend_sound_subtype = get_extender(SoundSubtype, lambda feature: {feature.to_sound_type()})
extend_place = get_extender(Place, lambda feature: {feature.to_place_category()})
extend_backness = get_extender(Backness, lambda feature: {feature.to_backness_category()})
extend_height = get_extender(Height, lambda feature: {feature.to_height_category()})
extend_airflow = get_extender(Airflow, lambda _: {SuprasegmentalType.AIRFLOW})
extend_intonation = get_extender(Intonation, lambda _: {SuprasegmentalType.INTONATION})
extend_stress_subtype = get_extender(StressSubtype, lambda feature: {feature.to_stress_type(),
                                                                     SuprasegmentalType.STRESS})
extend_tone_description = get_extender(Tone, lambda _: {ToneType.TONE_DESCRIPTION, SuprasegmentalType.TONE})
extend_tone_number = get_extender(ToneNumber, lambda _: {ToneType.TONE_NUMBER, SuprasegmentalType.TONE})
extend_tone_step = get_extender(ToneStep, lambda _: {ToneType.TONE_STEP, SuprasegmentalType.TONE})


def extend(features: set[Feature], extenders: list[FeatureExtender]) -> set[Feature]:
    features = features.copy()
    for extender in extenders:
        features = extender(features)
    return features


def apply_combining_data(data: CombiningData, combining: Combining, features: set[Feature]) -> Optional[set[Feature]]:
    transformations = data.get(combining, None)
    if transformations is None:
        return None
    result = features.copy()
    fit = False
    for feature, transformation in transformations:
        if feature in features:
            # Not "if feature in result": otherwise we would have {} -> {long} -> {extra-long} for a single 'ː'
            # as well as broken transformations of the form "C  f1  -f1, f2"
            result = transformation.apply(result)
            fit = True
    return result if fit else None


def apply_combining(combining: Combining, features: set[Feature]) -> Optional[set[Feature]]:
    return apply_combining_data(get_data().combining_recursive, combining, features)


def collect_consonant_features(consonants: LetterData) -> Iterator[SymbolWithFeatures]:
    for letter, features in consonants.items():
        yield letter, extend(features | {SymbolType.SOUND, SoundSubtype.SIMPLE_CONSONANT}, [
            extend_sound_subtype,
            extend_place,
        ])


def collect_vowel_features(vowels: LetterData) -> Iterator[SymbolWithFeatures]:
    for letter, features in vowels.items():
        yield letter, extend(features | {SymbolType.SOUND, SoundSubtype.SIMPLE_VOWEL}, [
            extend_sound_subtype,
            extend_backness,
            extend_height,
        ])


def collect_break_features(breaks: SymbolData) -> Iterator[SymbolWithFeatures]:
    for symbol, feature in breaks.items():
        yield symbol, {feature, SymbolType.BREAK}


def collect_suprasegmental_features(suprasegmentals: SymbolData) -> Iterator[SymbolWithFeatures]:
    for symbol, feature in suprasegmentals.items():
        yield symbol, extend({feature, SymbolType.SUPRASEGMENTAL}, [
            extend_airflow,
            extend_intonation,
            extend_stress_subtype,
            extend_tone_description,
            extend_tone_number,
            extend_tone_step,
        ])


def collect_basic_combined_features(combining_basic: CombiningData,
                                    non_combined: list[SymbolWithFeatures]) -> Iterator[SymbolWithFeatures]:
    for combining in combining_basic.keys():
        for symbol, features in non_combined:
            if (new_features := apply_combining_data(combining_basic, combining, features)) is not None:
                yield combining.apply(symbol), new_features


def collect_basic_features() -> dict[str, set[Feature]]:
    data = get_data()
    non_combined = list(chain(
        collect_consonant_features(data.consonants),
        collect_vowel_features(data.vowels),
        collect_break_features(data.breaks),
        collect_suprasegmental_features(data.suprasegmentals),
    ))
    combined = list(collect_basic_combined_features(data.combining_basic, non_combined))
    feature_index: dict[str, set[Feature]] = {}
    for symbol, features in non_combined + combined:
        if symbol in feature_index:
            raise DataError(f'Symbol "{symbol}" can be interpreted in multiple ways')
        feature_index[symbol] = features
    return feature_index


get_basic_features = with_cache(collect_basic_features)


def build_basic_matcher() -> Matcher:
    return Matcher(get_basic_features().keys())


get_basic_matcher = with_cache(build_basic_matcher)


def basic_symbol_to_features(symbol: str) -> Optional[set[Feature]]:
    return features[symbol].copy() if symbol in (features := get_basic_features()) else None


def unknown() -> set[Feature]:
    return {SymbolType.UNKNOWN}


def extract(features: set[Feature], *classes: Type[F]) -> set[F]:
    return {feature for feature in features if any(isinstance(feature, feature_class) for feature_class in classes)}


def combine_affricate(left: set[Feature], right: set[Feature]) -> Optional[set[Feature]]:
    if (extract(left, SoundSubtype, Manner) == {SoundSubtype.SIMPLE_CONSONANT, Manner.STOP}
            and extract(right, SoundSubtype, Manner) == {SoundSubtype.SIMPLE_CONSONANT, Manner.FRICATIVE}
            and left - {Manner.STOP} == right - {Manner.FRICATIVE, Manner.SIBILANT, Manner.LATERAL}):
        return ((left | right | {SoundSubtype.AFFRICATE_CONSONANT, Manner.AFFRICATE})
                - {SoundSubtype.SIMPLE_CONSONANT, Manner.STOP, Manner.FRICATIVE})
    else:
        return None


def combine_doubly_articulated(left: set[Feature], right: set[Feature]) -> Optional[set[Feature]]:
    def remove_place(features: set[Feature]) -> set[Feature]:
        return features - extend_place(extract(features, Place))

    if (extract(left, SoundSubtype) == {SoundSubtype.SIMPLE_CONSONANT} == extract(right, SoundSubtype)
            and extract(left, Place) != extract(right, Place)
            and remove_place(left) == remove_place(right)):
        return ((left | right | {SoundSubtype.DOUBLY_ARTICULATED_CONSONANT})
                - {SoundSubtype.SIMPLE_CONSONANT})
    else:
        return None


def combine_polyphthong(subtype: SoundSubtype, *feature_sets: set[Feature]) -> Optional[set[Feature]]:
    weak_syllabicity = {Syllabicity.NONSYLLABIC, Syllabicity.ANAPTYCTIC}
    if (all(extract(features, SoundSubtype) == {SoundSubtype.SIMPLE_VOWEL} for features in feature_sets)
            and any(extract(features, Syllabicity).isdisjoint(weak_syllabicity) for features in feature_sets)):
        return ((set().union(*feature_sets) | {subtype})
                - {SoundSubtype.SIMPLE_VOWEL} - weak_syllabicity)
    else:
        return None


def combine_diphthong(left: set[Feature], right: set[Feature]) -> Optional[set[Feature]]:
    return combine_polyphthong(SoundSubtype.DIPHTHONG_VOWEL, left, right)


def combine_triphthong(left: set[Feature], middle: set[Feature], right: set[Feature]) -> Optional[set[Feature]]:
    return combine_polyphthong(SoundSubtype.TRIPHTHONG_VOWEL, left, middle, right)


def combine_features(feature_sets: list[set[Feature]]) -> Optional[set[Feature]]:
    if len(feature_sets) <= 1:
        raise ValueError(f'Feature sets to combine should contain at least two sets (got {len(feature_sets)})')
    return next(
        (combined
         for combiner in {
             2: [
                 combine_affricate,
                 combine_doubly_articulated,
                 combine_diphthong,
             ],
             3: [
                 combine_triphthong,
             ],
         }.get(len(feature_sets), [])
         if (combined := combiner(*feature_sets)) is not None),
        None,
    )
