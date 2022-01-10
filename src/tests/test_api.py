from typing import Any
from unittest import main, TestCase

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
from ..ipaparser.features import Airflow, Voicing


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

    def test_symbol_features(self) -> None:
        unknown = 'unknown'

        with self.assertRaises(FeatureKindError) as context:
            IPASymbol('a').features(unknown)  # type: ignore
        self.assertEqual(context.exception.value, unknown)

        with self.assertRaises(FeatureKindError) as context:
            IPASymbol('a').features({Airflow, unknown, Voicing})  # type: ignore
        self.assertEqual(context.exception.value, unknown)

        with self.assertRaises(FeatureError) as context:
            IPASymbol('a').features(role=unknown)  # type: ignore
        self.assertEqual(context.exception.value, unknown)

    def test_operations(self) -> None:
        with self.assertRaises(IncompatibleTypesError):
            IPA('/a/') + IPA('[b]')


main()
