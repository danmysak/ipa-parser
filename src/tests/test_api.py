from typing import Any
from unittest import TestCase

from ..ipaparser import IPA, IPAConfig, IPASymbol
from ..ipaparser.definitions import BracketStrategy, TranscriptionType
from ..ipaparser.exceptions import (
    BracketStrategyError,
    CombinedLengthError,
    CombinedSoundError,
    EnclosingError,
    FeatureError,
    FeatureKindError,
    IncompatibleTypesError,
)
from ..ipaparser.features import Airflow, Height, HeightCategory, Manner, PlaceCategory, SoundType, SymbolType, Voicing


class TestApi(TestCase):
    def assertEqual(self, *values: Any) -> None:
        first, *rest = values
        for value in rest:
            super().assertEqual(first, value)

    def test_transcription_types(self) -> None:
        self.assertEqual(IPA('[a]').type, TranscriptionType.PHONETIC, 'phonetic')
        self.assertEqual(IPA('/a/').type, TranscriptionType.PHONEMIC, 'phonemic')
        self.assertEqual(IPA('⟨a⟩').type, TranscriptionType.LITERAL, 'literal')

        for transcription in ['abc', '(abc)', '[abc/']:
            with self.assertRaises(EnclosingError) as context:
                IPA(transcription)
            self.assertEqual(context.exception.transcription, transcription)

    def test_bracket_strategies(self) -> None:
        string = '[(a)bc((d)e)fg⁽ʰ⁾i(j)]'
        self.assertEqual(
            str(IPA(string, IPAConfig(brackets=BracketStrategy.KEEP))),
            str(IPA(string, IPAConfig(brackets='keep'))),  # type: ignore
            string,
        )
        self.assertEqual(
            str(IPA(string, IPAConfig(brackets=BracketStrategy.EXPAND))),
            str(IPA(string, IPAConfig(brackets='expand'))),  # type: ignore
            '[abcdefgʰij]',
        )
        self.assertEqual(
            str(IPA(string, IPAConfig(brackets=BracketStrategy.STRIP))),
            str(IPA(string, IPAConfig(brackets='strip'))),  # type: ignore
            '[bcfgi]',
        )

        with self.assertRaisesRegex(BracketStrategyError, r'keep/expand/strip') as context:
            IPAConfig(brackets='ignore')  # type: ignore
        self.assertEqual(context.exception.value, 'ignore')

    def test_combined(self) -> None:
        with self.assertRaises(CombinedLengthError) as context:
            IPAConfig(combined=[()])
        self.assertEqual(context.exception.sequence, ())

        with self.assertRaises(CombinedLengthError) as context:
            IPAConfig(combined=[('t', 's'), ('dz',), ('a', 'o', 'u')])
        self.assertEqual(context.exception.sequence, ('dz',))

        with self.assertRaises(CombinedSoundError) as context:
            IPAConfig(combined=[('t', 's'), ('d', '')])
        self.assertEqual(context.exception.sound, '')

        with self.assertRaises(CombinedSoundError) as context:
            IPAConfig(combined=[('d̥', 'z̥'), ('̥d', 'z')])
        self.assertEqual(context.exception.sound, '̥d')

        self.assertEqual(str(IPASymbol('ts', IPAConfig(combined=[('t', 's')]))), 't͡s')

    def test_symbol_features(self) -> None:
        unknown = 'unknown'

        with self.assertRaises(FeatureKindError) as context:
            IPASymbol('a').features(unknown)  # type: ignore
        self.assertEqual(context.exception.value, unknown)

        self.assertTrue(isinstance(IPASymbol('a').features(Height), frozenset))
        self.assertTrue(isinstance(IPASymbol('l').features({Manner, 'voicing'}), frozenset))

        self.assertEqual(
            IPASymbol('a').features(Height),
            IPASymbol('a').features('height', role='open'),  # type: ignore
            IPASymbol('a').features({Height}, role=SoundType.VOWEL),
            IPASymbol('a').features({'height'}),  # type: ignore
            IPASymbol('a').features(frozenset({Height})),
            IPASymbol('a').features(frozenset({'height'})),  # type: ignore
            IPASymbol('a').features({Height, Manner}, role='simple vowel'),  # type: ignore
            IPASymbol('a').features({'height', 'manner'}),  # type: ignore
            IPASymbol('a').features(frozenset({Height, Manner})),
            IPASymbol('a').features(frozenset({Height, 'manner'})),  # type: ignore
            {Height.OPEN},
        )
        self.assertEqual(
            IPASymbol('a').features({Height, HeightCategory}),
            IPASymbol('a').features(frozenset({'height', 'height category'}), role='about open'),  # type: ignore
            {Height.OPEN, HeightCategory.ABOUT_OPEN},
        )
        self.assertEqual(
            IPASymbol('l').features(Manner, role=SymbolType.SOUND),
            IPASymbol('l').features('manner'),  # type: ignore
            IPASymbol('l').features({Manner}, role='approximant'),  # type: ignore
            IPASymbol('l').features(frozenset({Manner})),
            IPASymbol('l').features({Height, Manner}),
            IPASymbol('l').features(frozenset({Height, Manner})),
            IPASymbol('l').features(frozenset({'height', 'manner'})),  # type: ignore
            {Manner.APPROXIMANT, Manner.LATERAL},
        )
        self.assertEqual(
            IPASymbol('l').features({'manner', 'voicing'}),  # type: ignore
            IPASymbol('l').features(frozenset({Manner, Voicing}), role=PlaceCategory.CORONAL),
            {Manner.APPROXIMANT, Manner.LATERAL, Voicing.VOICED},
        )
        self.assertEqual(
            IPASymbol('a').features(set()),
            IPASymbol('l').features(frozenset()),
            set(),
        )
        self.assertNotEqual(IPASymbol('a').features(), None)
        self.assertNotEqual(IPASymbol('l').features(), None)
        self.assertEqual(
            IPASymbol('a').features(role=SoundType.CONSONANT),
            IPASymbol('a').features({Height}, role='close'),  # type: ignore
            IPASymbol('l').features(role='high tone'),  # type: ignore
            IPASymbol('l').features({Manner, Voicing}, role=Height.OPEN),
            None,
        )

        with self.assertRaises(FeatureKindError) as context:
            IPASymbol('a').features({Airflow, unknown, Voicing})  # type: ignore
        self.assertEqual(context.exception.value, unknown)

        with self.assertRaises(FeatureError) as context:
            IPASymbol('a').features(role=unknown)  # type: ignore
        self.assertEqual(context.exception.value, unknown)

    def test_operations(self) -> None:
        with self.assertRaises(IncompatibleTypesError):
            IPA('/a/') + IPA('[b]')
