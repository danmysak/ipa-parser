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
    PlaceCategory,
    Release,
    Roundedness,
    SecondaryModifier,
    SecondaryPlace,
    SoundSubtype,
    Syllabicity,
    Voicing,
)

__all__ = [
    'combine_features',
    'interpret',
]


APPROXIMANTS_VS_VOWELS: list[list[tuple[set[Feature], set[Feature]]]] = [
    # General:
    [({
        SoundSubtype.SIMPLE_CONSONANT,
        Manner.APPROXIMANT,
    }, {
        SoundSubtype.SIMPLE_VOWEL,
        Height.CLOSE,
    })],
    # Syllabicity:
    [(set(
        # -
    ), {
        Syllabicity.NONSYLLABIC,
    }), ({
        Syllabicity.SYLLABIC,
    }, set(
        # -
    ))],
    # Voicing:
    [({
        Voicing.VOICED,
    }, set(
        # -
    )), (set(
        # -
    ), {
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
    }), (set(
        # -
    ), set(
        # -
    ))],
]


def alternative_type(features: FeatureSet) -> Iterator[FeatureSet]:
    affected_kinds = set(feature.__class__
                         for aspect in APPROXIMANTS_VS_VOWELS
                         for consonant_features, vowel_features in aspect
                         for feature in (consonant_features | vowel_features))

    def with_replaced(match: FeatureSet, replace: FeatureSet) -> Iterator[FeatureSet]:
        if include(affected_kinds, features) == match:
            yield (features - extend(match)) | extend(replace)

    for pairs in product(*APPROXIMANTS_VS_VOWELS):
        approximant, vowel = map(lambda sets: frozenset().union(*sets), zip(*pairs))
        yield from with_replaced(approximant, vowel)
        yield from with_replaced(vowel, approximant)


def alternative_coronal_place(features: FeatureSet) -> Iterator[FeatureSet]:
    if (include({Place}, features) == {Place.ALVEOLAR}
            and include({Manner}, features) - {Manner.SIBILANT} != {Manner.FRICATIVE}):
        for place in [Place.DENTAL, Place.POSTALVEOLAR]:
            yield exclude({Place}, features) | place.extend()


def interpret(features: FeatureSet) -> Iterator[FeatureSet]:
    yield features
    yield from alternative_type(features)
    yield from alternative_coronal_place(features)


def combine_affricate(left: FeatureSet, right: FeatureSet) -> Optional[FeatureSet]:
    def matching_places(left_places: FeatureSet, right_places: FeatureSet) -> bool:
        return left_places == right_places or (left_places, right_places) in [({Place.ALVEOLAR}, {Place.PALATAL}),
                                                                              ({Place.BILABIAL}, {Place.LABIODENTAL})]

    if (include({SoundSubtype, Manner}, left) - {Manner.EJECTIVE} == {SoundSubtype.SIMPLE_CONSONANT, Manner.STOP}
            and Manner.FRICATIVE in right
            and equivalent(left - {Manner.STOP, Manner.EJECTIVE},
                           right - {Manner.FRICATIVE, Manner.SIBILANT, Manner.LATERAL, Manner.EJECTIVE},
                           {SoundSubtype, Manner, Voicing})
            and matching_places(*(include({Place}, side) for side in (left, right)))):
        return ((left | right | {Manner.AFFRICATE})
                - {Manner.STOP, Manner.FRICATIVE})
    else:
        return None


def combine_doubly_articulated(left: FeatureSet, right: FeatureSet) -> Optional[FeatureSet]:
    if (include({SoundSubtype}, left) == {SoundSubtype.SIMPLE_CONSONANT}
            and equivalent(left - {Manner.EJECTIVE},
                           right - {Manner.EJECTIVE},
                           {SoundSubtype, Manner, Voicing})
            and not equivalent(left, right, {PlaceCategory})):
        return ((left | right | {SoundSubtype.DOUBLY_ARTICULATED_CONSONANT})
                - {SoundSubtype.SIMPLE_CONSONANT})
    else:
        return None


def combine_contour_click(left: FeatureSet, right: FeatureSet) -> Optional[FeatureSet]:
    if (include({SoundSubtype}, left) == {SoundSubtype.SIMPLE_CONSONANT}
            and Manner.CLICK in left
            and include({SoundSubtype, Place}, right) == {SoundSubtype.SIMPLE_CONSONANT, Place.UVULAR}):
        manners: dict[FeatureSet, Feature] = {
            frozenset({Manner.STOP}): Manner.STOP,
            frozenset({Manner.FRICATIVE}): Manner.AFFRICATE,
        }
        if (right_manner := include({Manner}, right - {Manner.EJECTIVE})) in manners:
            return ((left | (right - right_manner) | {SoundSubtype.CONTOUR_CLICK, manners[right_manner]})
                    - {SoundSubtype.SIMPLE_CONSONANT})
    return None


def combine_prenasalized(left: FeatureSet, right: FeatureSet) -> Optional[FeatureSet]:
    base_extended = extend(include({Place}, right) | {SoundSubtype.SIMPLE_CONSONANT, Manner.NASAL})
    if left == base_extended:
        return right | {SecondaryModifier.PRENASALIZED, SecondaryModifier.VOICELESSLY_PRENASALIZED}
    elif left == base_extended | Voicing.VOICED.extend():
        return right | {SecondaryModifier.PRENASALIZED}
    else:
        return None


def combine_release(left: FeatureSet, right: FeatureSet) -> Optional[FeatureSet]:
    if include({SoundSubtype, Manner, Release}, left) != {SoundSubtype.SIMPLE_CONSONANT, Manner.STOP}:
        return None
    if include({SoundSubtype, Manner, Voicing}, right) == {SoundSubtype.SIMPLE_CONSONANT, Manner.NASAL, Voicing.VOICED}:
        return left | {Release.NASAL_RELEASE}
    for features, release in [(
        {Place.ALVEOLAR, Manner.APPROXIMANT, Manner.LATERAL, Voicing.VOICED},
        Release.LATERAL_RELEASE,
    ), (
        {Place.DENTAL, Manner.FRICATIVE},
        Release.VOICELESS_DENTAL_FRICATIVE_RELEASE,
    ), (
        {Place.ALVEOLAR, Manner.SIBILANT, Manner.FRICATIVE},
        Release.VOICELESS_ALVEOLAR_SIBILANT_FRICATIVE_RELEASE,
    ), (
        {Place.VELAR, Manner.FRICATIVE},
        Release.VOICELESS_VELAR_FRICATIVE_RELEASE,
    )]:
        if right == extend(frozenset({SoundSubtype.SIMPLE_CONSONANT}) | features):
            return left | {release}
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
    return combine_polyphthong(SoundSubtype.DIPHTHONG, left, right)


def combine_triphthong(left: FeatureSet, middle: FeatureSet, right: FeatureSet) -> Optional[FeatureSet]:
    return combine_polyphthong(SoundSubtype.TRIPHTHONG, left, middle, right)


def combine_triple_left_to_right(left: FeatureSet, middle: FeatureSet, right: FeatureSet) -> Optional[FeatureSet]:
    if (left_middle := combine_features([left, middle])) is not None:
        return combine_features([left_middle, right])
    else:
        return None


def combine_triple_right_to_left(left: FeatureSet, middle: FeatureSet, right: FeatureSet) -> Optional[FeatureSet]:
    if (middle_right := combine_features([middle, right])) is not None:
        return combine_features([left, middle_right])
    else:
        return None


def combine_features(feature_sets: list[FeatureSet]) -> Optional[FeatureSet]:
    if len(feature_sets) <= 1:
        raise ValueError(f'Feature sets to combine should contain at least two sets (got {len(feature_sets)})')
    if combiners := {
        2: [
            combine_affricate,
            combine_diphthong,
            combine_doubly_articulated,
            combine_contour_click,
            combine_prenasalized,
            combine_release,
        ],
        3: [
            combine_triphthong,
            combine_triple_left_to_right,
            combine_triple_right_to_left,
        ],
    }.get(len(feature_sets), None):
        interpretations = list(product(*map(interpret, feature_sets)))
        return next(
            (combined
             for combiner in combiners
             for interpretation in interpretations
             if (combined := combiner(*interpretation)) is not None),
            None,
        )
    else:
        return None
