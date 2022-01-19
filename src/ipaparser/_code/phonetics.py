from itertools import product

from .feature_helper import equivalent, extend, include
from .features import (
    Feature,
    FeatureSet,
    Manner,
    Place,
    PlaceCategory,
    SecondaryModifier,
    SoundSubtype,
    Syllabicity,
    Voicing,
)

__all__ = [
    'combine_feature_sets',
]


def combine_affricate(left: FeatureSet, right: FeatureSet) -> list[FeatureSet]:
    def matching_places(left_places: FeatureSet, right_places: FeatureSet) -> bool:
        return left_places == right_places or (left_places, right_places) in [({Place.ALVEOLAR}, {Place.PALATAL}),
                                                                              ({Place.BILABIAL}, {Place.LABIODENTAL})]

    if (include({SoundSubtype, Manner}, left) - {Manner.EJECTIVE} == {SoundSubtype.SIMPLE_CONSONANT, Manner.STOP}
            and Manner.FRICATIVE in right
            and equivalent({SoundSubtype, Manner, Voicing},
                           left - {Manner.STOP, Manner.EJECTIVE},
                           right - {Manner.FRICATIVE, Manner.SIBILANT, Manner.LATERAL, Manner.EJECTIVE})
            and matching_places(*(include({Place}, side) for side in (left, right)))):
        return [((left | right | {Manner.AFFRICATE})
                 - {Manner.STOP, Manner.FRICATIVE})]
    else:
        return []


def combine_doubly_articulated(left: FeatureSet, right: FeatureSet) -> list[FeatureSet]:
    if (include({SoundSubtype}, left) == {SoundSubtype.SIMPLE_CONSONANT}
            and equivalent({SoundSubtype, Manner, Voicing},
                           left - {Manner.EJECTIVE},
                           right - {Manner.EJECTIVE})
            and not equivalent({PlaceCategory}, left, right)):
        return [((left | right | {SoundSubtype.DOUBLY_ARTICULATED_CONSONANT})
                 - {SoundSubtype.SIMPLE_CONSONANT})]
    else:
        return []


def combine_contour_click(left: FeatureSet, right: FeatureSet) -> list[FeatureSet]:
    if (include({SoundSubtype}, left) == {SoundSubtype.SIMPLE_CONSONANT}
            and Manner.CLICK in left
            and include({SoundSubtype, Place}, right) == {SoundSubtype.SIMPLE_CONSONANT, Place.UVULAR}):
        manners: dict[FeatureSet, Feature] = {
            frozenset({Manner.STOP}): Manner.STOP,
            frozenset({Manner.FRICATIVE}): Manner.AFFRICATE,
        }
        if (right_manner := include({Manner}, right - {Manner.EJECTIVE})) in manners:
            return [((left | (right - right_manner) | {SoundSubtype.CONTOUR_CLICK, manners[right_manner]})
                     - {SoundSubtype.SIMPLE_CONSONANT})]
    return []


def combine_prenasalized(left: FeatureSet, right: FeatureSet) -> list[FeatureSet]:
    base_extended = extend(include({Place}, right) | {SoundSubtype.SIMPLE_CONSONANT, Manner.NASAL})
    if left == base_extended:
        return [right | {SecondaryModifier.PRENASALIZED, SecondaryModifier.VOICELESSLY_PRENASALIZED}]
    elif left == base_extended | Voicing.VOICED.extend():
        return [right | {SecondaryModifier.PRENASALIZED}]
    else:
        return []


def combine_polyphthong(subtype: SoundSubtype, *feature_sets: FeatureSet) -> list[FeatureSet]:
    weak_syllabicity = {Syllabicity.NONSYLLABIC, Syllabicity.ANAPTYCTIC}
    if (all(include({SoundSubtype}, features) == {SoundSubtype.SIMPLE_VOWEL} for features in feature_sets)
            and any(features.isdisjoint(weak_syllabicity) for features in feature_sets)):
        return [((frozenset().union(*feature_sets) | {subtype})
                 - {SoundSubtype.SIMPLE_VOWEL} - weak_syllabicity)]
    else:
        return []


def combine_diphthong(left: FeatureSet, right: FeatureSet) -> list[FeatureSet]:
    return combine_polyphthong(SoundSubtype.DIPHTHONG, left, right)


def combine_triphthong(left: FeatureSet, middle: FeatureSet, right: FeatureSet) -> list[FeatureSet]:
    return combine_polyphthong(SoundSubtype.TRIPHTHONG, left, middle, right)


def combine_triple_left_to_right(left: FeatureSet, middle: FeatureSet, right: FeatureSet) -> list[FeatureSet]:
    return combine_feature_sets(combine_feature_sets([left], [middle]), [right])


def combine_triple_right_to_left(left: FeatureSet, middle: FeatureSet, right: FeatureSet) -> list[FeatureSet]:
    return combine_feature_sets([left], combine_feature_sets([middle], [right]))


COMBINERS = {
    2: [
        combine_affricate,
        combine_diphthong,
        combine_doubly_articulated,
        combine_contour_click,
        combine_prenasalized,
    ],
    3: [
        combine_triphthong,
        combine_triple_left_to_right,
        combine_triple_right_to_left,
    ],
}


def combine_feature_sets(*feature_sets: list[FeatureSet]) -> list[FeatureSet]:
    if len(feature_sets) <= 1:
        raise ValueError(f'There should be at least two lists of feature sets to combine (got {len(feature_sets)})')
    return [features
            for combiner in COMBINERS.get(len(feature_sets), [])
            for interpretation in product(*feature_sets)
            for features in combiner(*interpretation)]
