from functools import partial
from typing import Callable, Optional, Union
from unittest import TestCase

from ..ipaparser.features import (
    Airflow,
    Articulation,
    Aspiration,
    Backness,
    BacknessCategory,
    BreakType,
    Feature,
    FEATURE_KINDS,
    FeatureSet,
    Height,
    HeightCategory,
    Intonation,
    Length,
    Manner,
    Phonation,
    Place,
    PlaceCategory,
    Release,
    Roundedness,
    RoundednessModifier,
    SecondaryModifier,
    SecondaryPlace,
    SoundSubtype,
    SoundType,
    Strength,
    StressSubtype,
    StressType,
    SuprasegmentalType,
    Syllabicity,
    SymbolType,
    Tone,
    ToneLetter,
    ToneNumber,
    ToneStep,
    ToneType,
    Voicing,
)

__all__ = [
    'TestFeatures',
]


def find_category(values_by_category: dict[str, list[str]], value: str) -> str:
    for category, values in values_by_category.items():
        if value in values:
            return category
    assert False


class TestFeatures(TestCase):
    def _test_values(self,
                     values: list[tuple[Feature, str]],
                     derived: Optional[Union[Feature, Callable[[Feature], str]]] = None,
                     extra_derived: Optional[set[str]] = None) -> None:
        assert values
        feature_kind = values[0][0].__class__
        assert all(feature.__class__ == feature_kind for feature, _ in values)
        self.assertEqual(len(set(feature for feature, _ in values)), len(feature_kind))
        for feature, name in values:
            self.assertEqual(feature, name)
            derived_feature = derived(feature) if callable(derived) else derived
            self.assertEqual(feature.derived(), derived_feature)
            self.assertEqual(
                feature.extend(),
                {feature} | ({derived_feature} if derived_feature else set()) | (extra_derived or set()),
            )

    def test_airflow(self) -> None:
        self._test_values(
            [
                (Airflow.EGRESSIVE_AIRFLOW, 'egressive airflow'),
                (Airflow.INGRESSIVE_AIRFLOW, 'ingressive airflow'),
            ],
            SuprasegmentalType.AIRFLOW,
            {SymbolType.SUPRASEGMENTAL},
        )

    def test_articulation(self) -> None:
        self._test_values([
            (Articulation.APICAL, 'apical'),
            (Articulation.LAMINAL, 'laminal'),
            (Articulation.ADVANCED, 'advanced'),
            (Articulation.RETRACTED, 'retracted'),
            (Articulation.CENTRALIZED, 'centralized'),
            (Articulation.MID_CENTRALIZED, 'mid-centralized'),
            (Articulation.RAISED, 'raised'),
            (Articulation.LOWERED, 'lowered'),
        ])

    def test_aspiration(self) -> None:
        self._test_values([
            (Aspiration.ASPIRATED, 'aspirated'),
            (Aspiration.UNASPIRATED, 'unaspirated'),
            (Aspiration.PREASPIRATED, 'preaspirated'),
        ])

    def test_backness(self) -> None:
        self._test_values([
            (BacknessCategory.ABOUT_FRONT, 'about front'),
            (BacknessCategory.ABOUT_CENTRAL, 'about central'),
            (BacknessCategory.ABOUT_BACK, 'about back'),
        ])

        self._test_values(
            [
                (Backness.FRONT, 'front'),
                (Backness.NEAR_FRONT, 'near-front'),
                (Backness.CENTRAL, 'central'),
                (Backness.NEAR_BACK, 'near-back'),
                (Backness.BACK, 'back'),
            ],
            partial(find_category, {
                'about front': ['front', 'near-front'],
                'about central': ['central'],
                'about back': ['near-back', 'back'],
            }),
        )

    def test_breaks(self) -> None:
        self._test_values(
            [
                (BreakType.SPACE, 'space'),
                (BreakType.HYPHEN, 'hyphen'),
                (BreakType.LINKING, 'linking'),
                (BreakType.SYLLABLE_BREAK, 'syllable break'),
                (BreakType.MINOR_BREAK, 'minor break'),
                (BreakType.MAJOR_BREAK, 'major break'),
                (BreakType.EQUIVALENCE, 'equivalence'),
                (BreakType.ELLIPSIS, 'ellipsis'),
            ],
            SymbolType.BREAK,
        )

    def test_height(self) -> None:
        self._test_values([
            (HeightCategory.ABOUT_CLOSE, 'about close'),
            (HeightCategory.ABOUT_MID, 'about mid'),
            (HeightCategory.ABOUT_OPEN, 'about open'),
        ])

        self._test_values(
            [
                (Height.CLOSE, 'close'),
                (Height.NEAR_CLOSE, 'near-close'),
                (Height.CLOSE_MID, 'close-mid'),
                (Height.MID, 'mid'),
                (Height.OPEN_MID, 'open-mid'),
                (Height.NEAR_OPEN, 'near-open'),
                (Height.OPEN, 'open'),
            ],
            partial(find_category, {
                'about close': ['close', 'near-close'],
                'about mid': ['close-mid', 'mid', 'open-mid'],
                'about open': ['near-open', 'open'],
            }),
        )

    def test_intonation(self) -> None:
        self._test_values(
            [
                (Intonation.GLOBAL_RISE, 'global rise'),
                (Intonation.GLOBAL_FALL, 'global fall'),
            ],
            SuprasegmentalType.INTONATION,
            {SymbolType.SUPRASEGMENTAL},
        )

    def test_length(self) -> None:
        self._test_values([
            (Length.EXTRA_SHORT, 'extra-short'),
            (Length.HALF_LONG, 'half-long'),
            (Length.LONG, 'long'),
            (Length.EXTRA_LONG, 'extra-long'),
        ])

    def test_manner(self) -> None:
        self._test_values([
            (Manner.AFFRICATE, 'affricate'),
            (Manner.APPROXIMANT, 'approximant'),
            (Manner.FRICATIVE, 'fricative'),
            (Manner.LATERAL, 'lateral'),
            (Manner.NASAL, 'nasal'),
            (Manner.SIBILANT, 'sibilant'),
            (Manner.STOP, 'stop'),
            (Manner.TAP_FLAP, 'tap/flap'),
            (Manner.TRILL, 'trill'),
            (Manner.CLICK, 'click'),
            (Manner.EJECTIVE, 'ejective'),
            (Manner.IMPLOSIVE, 'implosive'),
        ])

    def test_place(self) -> None:
        self._test_values([
            (PlaceCategory.LABIAL, 'labial'),
            (PlaceCategory.CORONAL, 'coronal'),
            (PlaceCategory.DORSAL, 'dorsal'),
            (PlaceCategory.LARYNGEAL, 'laryngeal'),
        ])

        self._test_values(
            [
                (Place.BILABIAL, 'bilabial'),
                (Place.LABIODENTAL, 'labiodental'),
                (Place.LINGUOLABIAL, 'linguolabial'),
                (Place.DENTAL, 'dental'),
                (Place.ALVEOLAR, 'alveolar'),
                (Place.POSTALVEOLAR, 'postalveolar'),
                (Place.RETROFLEX, 'retroflex'),
                (Place.PALATAL, 'palatal'),
                (Place.VELAR, 'velar'),
                (Place.UVULAR, 'uvular'),
                (Place.PHARYNGEAL_EPIGLOTTAL, 'pharyngeal/epiglottal'),
                (Place.GLOTTAL, 'glottal'),
            ],
            partial(find_category, {
                'labial': ['bilabial', 'labiodental'],
                'coronal': ['linguolabial', 'dental', 'alveolar', 'postalveolar', 'retroflex'],
                'dorsal': ['palatal', 'velar', 'uvular'],
                'laryngeal': ['pharyngeal/epiglottal', 'glottal'],
            }),
        )

    def test_release(self) -> None:
        self._test_values([
            (Release.NO_AUDIBLE_RELEASE, 'no audible release'),
            (Release.NASAL_RELEASE, 'nasal release'),
            (Release.LATERAL_RELEASE, 'lateral release'),
            (Release.VOICELESS_DENTAL_FRICATIVE_RELEASE, 'voiceless dental fricative release'),
            (Release.VOICELESS_ALVEOLAR_SIBILANT_FRICATIVE_RELEASE, 'voiceless alveolar sibilant fricative release'),
            (Release.VOICELESS_VELAR_FRICATIVE_RELEASE, 'voiceless velar fricative release'),
        ])

    def test_roundedness(self) -> None:
        self._test_values([
            (Roundedness.ROUNDED, 'rounded'),
        ])

        self._test_values([
            (RoundednessModifier.MORE_ROUNDED, 'more rounded'),
            (RoundednessModifier.LESS_ROUNDED, 'less rounded'),
            (RoundednessModifier.COMPRESSED, 'compressed'),
            (RoundednessModifier.LABIAL_SPREADING, 'labial spreading'),
        ])

    def test_secondary(self) -> None:
        self._test_values([
            (SecondaryPlace.LABIALIZED, 'labialized'),
            (SecondaryPlace.PALATALIZED, 'palatalized'),
            (SecondaryPlace.VELARIZED, 'velarized'),
            (SecondaryPlace.PHARYNGEALIZED, 'pharyngealized'),
            (SecondaryPlace.GLOTTALIZED, 'glottalized'),
        ])

        self._test_values([
            (SecondaryModifier.ADVANCED_TONGUE_ROOT, 'advanced tongue root'),
            (SecondaryModifier.RETRACTED_TONGUE_ROOT, 'retracted tongue root'),
            (SecondaryModifier.R_COLORED, 'r-colored'),
            (SecondaryModifier.NASALIZED, 'nasalized'),
            (SecondaryModifier.PRENASALIZED, 'prenasalized'),
            (SecondaryModifier.VOICELESSLY_PRENASALIZED, 'voicelessly prenasalized'),
            (SecondaryModifier.PRESTOPPED, 'prestopped'),
            (SecondaryModifier.PREGLOTTALIZED, 'preglottalized'),
        ])

    def test_sound(self) -> None:
        self._test_values(
            [
                (SoundType.CONSONANT, 'consonant'),
                (SoundType.VOWEL, 'vowel'),
            ],
            SymbolType.SOUND,
        )

        self._test_values(
            [
                (SoundSubtype.SIMPLE_CONSONANT, 'simple consonant'),
                (SoundSubtype.DOUBLY_ARTICULATED_CONSONANT, 'doubly articulated consonant'),
                (SoundSubtype.CONTOUR_CLICK, 'contour click'),
                (SoundSubtype.SIMPLE_VOWEL, 'simple vowel'),
                (SoundSubtype.DIPHTHONG, 'diphthong'),
                (SoundSubtype.TRIPHTHONG, 'triphthong'),
            ],
            partial(find_category, {
                'consonant': ['simple consonant', 'doubly articulated consonant', 'contour click'],
                'vowel': ['simple vowel', 'diphthong', 'triphthong'],
            }),
            {SymbolType.SOUND},
        )

    def test_strength(self) -> None:
        self._test_values([
            (Strength.STRONG, 'strong'),
            (Strength.WEAK, 'weak'),
        ])

    def test_stress(self) -> None:
        self._test_values(
            [
                (StressType.PRIMARY_STRESS, 'primary stress'),
                (StressType.SECONDARY_STRESS, 'secondary stress'),
            ],
            SuprasegmentalType.STRESS,
            {SymbolType.SUPRASEGMENTAL},
        )

        self._test_values(
            [
                (StressSubtype.REGULAR_PRIMARY_STRESS, 'regular primary stress'),
                (StressSubtype.EXTRA_STRONG_PRIMARY_STRESS, 'extra-strong primary stress'),
                (StressSubtype.REGULAR_SECONDARY_STRESS, 'regular secondary stress'),
                (StressSubtype.EXTRA_WEAK_SECONDARY_STRESS, 'extra-weak secondary stress'),
            ],
            partial(find_category, {
                'primary stress': ['regular primary stress', 'extra-strong primary stress'],
                'secondary stress': ['regular secondary stress', 'extra-weak secondary stress'],
            }),
            {SuprasegmentalType.STRESS, SymbolType.SUPRASEGMENTAL},
        )

    def test_suprasegmental(self) -> None:
        self._test_values(
            [
                (SuprasegmentalType.STRESS, 'stress'),
                (SuprasegmentalType.TONE, 'tone'),
                (SuprasegmentalType.INTONATION, 'intonation'),
                (SuprasegmentalType.AIRFLOW, 'airflow'),
            ],
            SymbolType.SUPRASEGMENTAL,
        )

    def test_syllabicity(self) -> None:
        self._test_values([
            (Syllabicity.SYLLABIC, 'syllabic'),
            (Syllabicity.NONSYLLABIC, 'nonsyllabic'),
            (Syllabicity.ANAPTYCTIC, 'anaptyctic'),
        ])

    def test_symbol(self) -> None:
        self._test_values([
            (SymbolType.SOUND, 'sound'),
            (SymbolType.BREAK, 'break'),
            (SymbolType.SUPRASEGMENTAL, 'suprasegmental'),
        ])

    def test_tone(self) -> None:
        self._test_values([
            (Tone.EXTRA_HIGH_TONE, 'extra-high tone'),
            (Tone.HIGH_TONE, 'high tone'),
            (Tone.MID_TONE, 'mid tone'),
            (Tone.LOW_TONE, 'low tone'),
            (Tone.EXTRA_LOW_TONE, 'extra-low tone'),
            (Tone.RISING_TONE, 'rising tone'),
            (Tone.FALLING_TONE, 'falling tone'),
            (Tone.HIGH_MID_RISING_TONE, 'high/mid rising tone'),
            (Tone.LOW_RISING_TONE, 'low rising tone'),
            (Tone.HIGH_FALLING_TONE, 'high falling tone'),
            (Tone.LOW_MID_FALLING_TONE, 'low/mid falling tone'),
            (Tone.PEAKING_TONE, 'peaking tone'),
            (Tone.DIPPING_TONE, 'dipping tone'),
        ])

        self._test_values(
            [
                (ToneType.TONE_LETTER, 'tone letter'),
                (ToneType.TONE_NUMBER, 'tone number'),
                (ToneType.TONE_STEP, 'tone step'),
            ],
            SuprasegmentalType.TONE,
            {SymbolType.SUPRASEGMENTAL},
        )

        self._test_values(
            [
                (ToneLetter.HIGH_TONE_LETTER, 'high tone letter'),
                (ToneLetter.HALF_HIGH_TONE_LETTER,  'half-high tone letter'),
                (ToneLetter.MID_TONE_LETTER, 'mid tone letter'),
                (ToneLetter.HALF_LOW_TONE_LETTER, 'half-low tone letter'),
                (ToneLetter.LOW_TONE_LETTER, 'low tone letter'),
            ],
            ToneType.TONE_LETTER,
            {SuprasegmentalType.TONE, SymbolType.SUPRASEGMENTAL},
        )

        self._test_values(
            [
                (ToneNumber.TONE_0, 'tone 0'),
                (ToneNumber.TONE_1, 'tone 1'),
                (ToneNumber.TONE_2, 'tone 2'),
                (ToneNumber.TONE_3, 'tone 3'),
                (ToneNumber.TONE_4, 'tone 4'),
                (ToneNumber.TONE_5, 'tone 5'),
                (ToneNumber.TONE_6, 'tone 6'),
                (ToneNumber.TONE_7, 'tone 7'),
                (ToneNumber.TONE_NUMBER_SEPARATOR, 'tone number separator'),
            ],
            ToneType.TONE_NUMBER,
            {SuprasegmentalType.TONE, SymbolType.SUPRASEGMENTAL},
        )

        self._test_values(
            [
                (ToneStep.UPSTEP, 'upstep'),
                (ToneStep.DOWNSTEP, 'downstep'),
            ],
            ToneType.TONE_STEP,
            {SuprasegmentalType.TONE, SymbolType.SUPRASEGMENTAL},
        )

    def test_voice(self) -> None:
        self._test_values([
            (Voicing.VOICED, 'voiced'),
            (Voicing.DEVOICED, 'devoiced'),
        ])

        self._test_values([
            (Phonation.BREATHY, 'breathy'),
            (Phonation.CREAKY, 'creaky'),
            (Phonation.WHISPERY, 'whispery'),
        ])

    def test_feature_set(self) -> None:
        self.assertEqual(FeatureSet, frozenset[Feature])

    def test_feature_kinds(self) -> None:
        self.assertEqual(FEATURE_KINDS, [
            Airflow,
            Articulation,
            Aspiration,
            Backness,
            BacknessCategory,
            BreakType,
            Height,
            HeightCategory,
            Intonation,
            Length,
            Manner,
            Phonation,
            Place,
            PlaceCategory,
            Release,
            Roundedness,
            RoundednessModifier,
            SecondaryModifier,
            SecondaryPlace,
            SoundSubtype,
            SoundType,
            Strength,
            StressSubtype,
            StressType,
            SuprasegmentalType,
            Syllabicity,
            SymbolType,
            Tone,
            ToneLetter,
            ToneNumber,
            ToneStep,
            ToneType,
            Voicing,
        ])
