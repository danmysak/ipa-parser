from itertools import product
from typing import Iterator, Optional

from .feature_helper import equivalent, exclude, extend, include
from .features import (
    Articulation,
    Backness,
    Feature,
    FeatureSet,
    Height,
    Manner,
    Place,
    Release,
    Roundedness,
    SecondaryPlace,
    SoundSubtype,
    Strength,
    Syllabicity,
    Voicing,
)

__all__ = [
    'combine_features',
    'interpret',
]


APPROXIMANTS_VS_NONSYLLABIC_VOWELS: list[list[tuple[set[Feature], set[Feature]]]] = [
    # General:
    [({
        SoundSubtype.SIMPLE_CONSONANT,
        Manner.APPROXIMANT,
    }, {
        SoundSubtype.SIMPLE_VOWEL,
        Syllabicity.NONSYLLABIC,
        Height.CLOSE,
    })],
    # Voicing:
    [({
        Voicing.VOICED,
    }, {
        # -
    }), ({
        # -
    }, {
        Voicing.DEVOICED,
    })],
    # Place/backness:
    [({
        Place.PALATAL,
    }, {
        Backness.FRONT,
    }), ({
        Place.PALATAL,
        Articulation.RETRACTED,
    }, {
        Backness.CENTRAL,
    }), ({
        Place.VELAR,
    }, {
        Backness.BACK,
    })],
    # Labialization/roundedness:
    [({
        SecondaryPlace.LABIALIZED,
    }, {
        Roundedness.ROUNDED,
    }), ({
        # -
    }, {
        # -
    })],
]


def alternative_type(features: FeatureSet) -> Iterator[FeatureSet]:
    for pairs in product(*APPROXIMANTS_VS_NONSYLLABIC_VOWELS):
        approximant, nonsyllabic_vowel = map(extend, map(lambda sets: frozenset().union(*sets), zip(*pairs)))
        if features == approximant:
            yield nonsyllabic_vowel
        elif features == nonsyllabic_vowel:
            yield approximant


def alternative_coronal_place(features: FeatureSet) -> Iterator[FeatureSet]:
    if include({Place}, features) == {Place.ALVEOLAR}:
        for place in [Place.DENTAL, Place.POSTALVEOLAR]:
            yield exclude({Place}, features) | place.extend()


def interpret(features: FeatureSet) -> Iterator[FeatureSet]:
    yield features
    yield from alternative_type(features)
    yield from alternative_coronal_place(features)


def combine_affricate(left: FeatureSet, right: FeatureSet) -> Optional[FeatureSet]:
    def matching_places(left_places: FeatureSet, right_places: FeatureSet) -> bool:
        return left_places == right_places or (left_places == {Place.ALVEOLAR} and right_places == {Place.PALATAL})

    if (include({SoundSubtype, Manner}, left) == {SoundSubtype.SIMPLE_CONSONANT, Manner.STOP}
            and Manner.FRICATIVE in right
            and equivalent(left - {Manner.STOP}, right - {Manner.FRICATIVE, Manner.SIBILANT, Manner.LATERAL},
                           excluded={Place, Articulation, Strength})  # t͡s̻ in Basque, t͡ɕ͈ in Korean
            and matching_places(*(include({Place}, side) for side in (left, right)))):
        return ((left | right | {SoundSubtype.AFFRICATE_CONSONANT, Manner.AFFRICATE})
                - {SoundSubtype.SIMPLE_CONSONANT, Manner.STOP, Manner.FRICATIVE})
    else:
        return None


def combine_doubly_articulated(left: FeatureSet, right: FeatureSet) -> Optional[FeatureSet]:
    if (include({SoundSubtype}, left) == {SoundSubtype.SIMPLE_CONSONANT}
            and equivalent(left, right, excluded={Place, Release})  # k͡p̚ in Vietnamese
            and not equivalent(left, right, included={Place})):
        return ((left | right | {SoundSubtype.DOUBLY_ARTICULATED_CONSONANT})
                - {SoundSubtype.SIMPLE_CONSONANT})
    else:
        return None


def combine_polyphthong(subtype: SoundSubtype, *feature_sets: FeatureSet) -> Optional[FeatureSet]:
    weak_syllabicity = {Syllabicity.NONSYLLABIC, Syllabicity.ANAPTYCTIC}
    if (all(include({SoundSubtype}, features) == {SoundSubtype.SIMPLE_VOWEL} for features in feature_sets)
            and any(features.isdisjoint(weak_syllabicity) for features in feature_sets)):
        return ((frozenset().union(*feature_sets) | {subtype})
                - {SoundSubtype.SIMPLE_VOWEL} - weak_syllabicity)
    else:
        return None


def combine_diphthong(left: FeatureSet, right: FeatureSet) -> Optional[FeatureSet]:
    return combine_polyphthong(SoundSubtype.DIPHTHONG_VOWEL, left, right)


def combine_triphthong(left: FeatureSet, middle: FeatureSet, right: FeatureSet) -> Optional[FeatureSet]:
    return combine_polyphthong(SoundSubtype.TRIPHTHONG_VOWEL, left, middle, right)


def combine_features(feature_sets: list[FeatureSet]) -> Optional[FeatureSet]:
    if len(feature_sets) <= 1:
        raise ValueError(f'Feature sets to combine should contain at least two sets (got {len(feature_sets)})')
    return next(
        (combined
         for interpretation in product(*map(interpret, feature_sets))
         for combiner in {
             2: [
                 combine_affricate,
                 combine_doubly_articulated,
                 combine_diphthong,
             ],
             3: [
                 combine_triphthong,
             ],
         }.get(len(interpretation), [])
         if (combined := combiner(*interpretation)) is not None),
        None,
    )
