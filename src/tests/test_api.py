from typing import Any, Optional
import unicodedata
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
from ..ipaparser.features import (
    Airflow,
    Feature,
    FeatureSet,
    Height,
    HeightCategory,
    Manner,
    PlaceCategory,
    SoundType,
    SymbolType,
    Voicing,
)


def to_features(ipa: IPA) -> list[Optional[FeatureSet]]:
    return [symbol.features() for symbol in ipa]


class TestApi(TestCase):
    def assertEqual(self, *values: Any) -> None:
        first, *rest = values
        for value in rest:
            super().assertEqual(first, value)

    def test_enclosing(self) -> None:
        self.assertEqual(IPA('[a]').type, TranscriptionType.PHONETIC, 'phonetic')
        self.assertEqual(IPA('[a]').left_bracket, '[')
        self.assertEqual(IPA('[a]').right_bracket, ']')

        self.assertEqual(IPA('/a/').type, TranscriptionType.PHONEMIC, 'phonemic')
        self.assertEqual(IPA('/a/').left_bracket, '/')
        self.assertEqual(IPA('/a/').right_bracket, '/')

        self.assertEqual(IPA('⟨a⟩').type, TranscriptionType.LITERAL, 'literal')
        self.assertEqual(IPA('⟨a⟩').left_bracket, '⟨')
        self.assertEqual(IPA('⟨a⟩').right_bracket, '⟩')

        for transcription in ['abc', '(abc)', '[abc/', '/abc', 'abc]', '/', '']:
            with self.assertRaises(EnclosingError) as context:
                IPA(transcription)
            self.assertEqual(context.exception.transcription, transcription)

    def test_bracket_strategies(self) -> None:
        strings = [
            ('[(a)bc((d)e)fg⁽ʰ⁾i(j)]', '[abcdefgʰij]', '[bcfgi]'),
            ('//', '//', '//'),
            ('[abc]', '[abc]', '[abc]'),
            ('/a(b)c.a)b(c.a(b)c/', '/abc.abc.abc/', '/ac.a)b(c.ac/'),
        ]
        for string, expanded, stripped in strings:
            self.assertEqual(
                str(IPA(string, IPAConfig(brackets=BracketStrategy.KEEP))),
                str(IPA(string, IPAConfig(brackets='keep'))),  # type: ignore
                string,
            )
            self.assertEqual(
                str(IPA(string, IPAConfig(brackets=BracketStrategy.EXPAND))),
                str(IPA(string, IPAConfig(brackets='expand'))),  # type: ignore
                expanded,
            )
            self.assertEqual(
                str(IPA(string, IPAConfig(brackets=BracketStrategy.STRIP))),
                str(IPA(string, IPAConfig(brackets='strip'))),  # type: ignore
                stripped,
            )
        self.assertFalse(IPA('[a(b)c]', IPAConfig(brackets=BracketStrategy.KEEP))[1].is_known())
        self.assertTrue(IPA('[a(b)c]', IPAConfig(brackets=BracketStrategy.KEEP))[2].is_known())
        self.assertFalse(IPA('[a(b)c]', IPAConfig(brackets=BracketStrategy.KEEP))[3].is_known())

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
        self.assertEqual(str(IPA('⟨tstːsːts⟩', IPAConfig(combined=[('tː', 'sː')]))), '⟨tstː͡sːts⟩')

        composed = 'ú'
        decomposed = 'ú'
        assert len(composed) == 1
        assert len(decomposed) == 2
        self.assertEqual(
            IPA(f'[a{composed}]', IPAConfig(combined=[('a', decomposed)])),
            IPA(f'[a{decomposed}]', IPAConfig(combined=[('a', composed)])),
            IPA(f'[a{composed}]', IPAConfig(combined=[('a', composed)])),
            IPA(f'[a{decomposed}]', IPAConfig(combined=[('a', decomposed)])),
            f'[a͡{decomposed}]',
        )

        latin = 'g'
        valid = 'ɡ'
        assert latin != valid
        for (transcription_letter, combined_letter, substitutions), (result_letter, result_length) in [
            ((latin, latin, False), (latin, 1)),
            ((latin, latin, True), (valid, 1)),
            ((latin, valid, False), (latin, 2)),
            ((latin, valid, True), (valid, 1)),
            ((valid, latin, False), (valid, 2)),
            ((valid, latin, True), (valid, 1)),
            ((valid, valid, False), (valid, 1)),
            ((valid, valid, True), (valid, 1)),
        ]:
            ipa = IPA(f'/{transcription_letter}b/',
                      IPAConfig(combined=[(combined_letter, 'b')], substitutions=substitutions))
            self.assertEqual(ipa, f'/{result_letter}{"͡" if result_length == 1 else ""}b/')
            self.assertEqual(len(ipa), result_length)
            self.assertEqual(ipa[0].is_known(), result_letter == valid)

        for letter in ['t', 'ʈ']:
            for mark in [':', 'ː']:
                self.assertEqual(
                    IPA(f'[{letter}{mark}ʂ]', IPAConfig(combined=[(f'{letter}{mark}', 'ʂ')], substitutions=True)),
                    '[ʈː͡ʂ]',
                )

        latin = 'g'
        valid = 'ɡ'
        assert latin != valid
        tone = '́'
        syllabicity = '̩'
        latin_tone = unicodedata.normalize('NFC', latin + tone)
        assert len(latin_tone) == 1
        for combined in [
            valid + tone + syllabicity,
            valid + syllabicity + tone,
            latin + tone + syllabicity,
            latin + syllabicity + tone,
            latin_tone + syllabicity,
        ]:
            self.assertEqual(
                IPA(f'/a{latin_tone}{syllabicity}bc/', IPAConfig(combined=[(combined, 'b')], substitutions=True)),
                f'/a{valid}{syllabicity}{tone}͡bc/',
            )

        self.assertEqual(
            IPA('[aɪ̯ aɪ ɔɪ̯ ɔɪ aʊ̯ aʊ]', IPAConfig(combined=[('a', 'ɪ̯'), ('a', 'ʊ̯'), ('ɔ', 'ɪ̯')])),
            '[a͡ɪ̯ aɪ ɔ͡ɪ̯ ɔɪ a͡ʊ̯ aʊ]',
        )
        self.assertEqual(
            IPA('[aɪ̯ aɪ ɔɪ̯ ɔɪ aʊ̯ aʊ]', IPAConfig(combined=[('a', 'ɪ'), ('a', 'ʊ'), ('ɔ', 'ɪ')])),
            '[aɪ̯ a͡ɪ ɔɪ̯ ɔ͡ɪ aʊ̯ a͡ʊ]',
        )
        self.assertEqual(
            IPA('[aɪ̯ a͜ɪ ɔɪ̯ ɔɪ a͡ʊ̯ aʊ]', IPAConfig(combined=[('a', 'ɪ̯'), ('a', 'ʊ̯'), ('ɔ', 'ɪ̯'),
                                                                ('a', 'ɪ'), ('a', 'ʊ'), ('ɔ', 'ɪ')])),
            '[a͡ɪ̯ a͜ɪ ɔ͡ɪ̯ ɔ͡ɪ a͡ʊ̯ a͡ʊ]',
        )
        self.assertEqual(IPA('[aɪ ɪa]', IPAConfig(combined=[('a', 'ɪ')])), '[a͡ɪ ɪa]')
        self.assertEqual(IPA('[aɪ a̯ɪ aɪ̯ a̯ɪ̯]', IPAConfig(combined=[('a', 'ɪ')])), '[a͡ɪ a̯ɪ aɪ̯ a̯ɪ̯]')
        self.assertEqual(IPA('[aɪ a̯ɪ aɪ̯ a̯ɪ̯]', IPAConfig(combined=[('a̯', 'ɪ')])), '[aɪ a̯͡ɪ aɪ̯ a̯ɪ̯]')
        self.assertEqual(IPA('[aɪ a̯ɪ aɪ̯ a̯ɪ̯]', IPAConfig(combined=[('a', 'ɪ̯')])), '[aɪ a̯ɪ a͡ɪ̯ a̯ɪ̯]')
        self.assertEqual(IPA('[aɪ a̯ɪ aɪ̯ a̯ɪ̯]', IPAConfig(combined=[('a̯', 'ɪ̯')])), '[aɪ a̯ɪ aɪ̯ a̯͡ɪ̯]')

        for transcription in [
            '[a̯ɪ̯̊]',
            '[å̯ɪ̯]',
            '[å̯ɪ̯̊]',
            '[åɪ̯]',
            '[a̯ɪ̊]',
            '[åɪ̊]',
        ]:
            for combined in [
                [('a', 'ɪ')],
                [('a̯', 'ɪ')],
                [('a', 'ɪ̯')],
                [('a̯', 'ɪ̯')],
            ]:
                self.assertEqual(IPA(transcription, IPAConfig(combined=combined)), transcription)

        self.assertEqual(
            IPA('/ntsnttsns=nts=ouaoauaou/', IPAConfig(combined=[('n', 't', 's'), ('a', 'o', 'u')])),
            '/n͡t͡snttsns=n͡t͡s=ouaoaua͡o͡u/',
        )
        self.assertEqual(
            IPA('/ntsau/', IPAConfig(combined=[('a', 'u'), ('n', 't', 's')])),
            '/n͡t͡sa͡u/',
        )
        self.assertEqual(
            IPA('/nts/', IPAConfig(combined=[('n', 't'), ('t', 's')])),
            IPA('/nts/', IPAConfig(combined=[('t', 's'), ('n', 't')])),
            '/n͡t͡s/',
        )
        for transcription, result in [
            ('/n͡ts/', '/n͡t͡s/'),
            ('/nt͡s/', '/n͡t͡s/'),
            ('/n͜ts/', '/n͜t͡s/'),
            ('/nt͜s/', '/n͡t͜s/'),
        ]:
            for combined in [
                [('n', 't'), ('t', 's')],
                [('t', 's'), ('n', 't')],
            ]:
                self.assertEqual(IPA(transcription, IPAConfig(combined=combined)), result)
        self.assertEqual(IPA('/nt͡snts/', IPAConfig(combined=[('n', 't͡s')])), '/n͡t͡snts/')
        self.assertEqual(IPA('/nt͡snts/', IPAConfig(combined=[('n', 'ts')])), '/nt͡sn͡ts/')
        self.assertEqual(IPA('/aoua͡ou/', IPAConfig(combined=[('a͡o', 'u')])), '/aoua͡o͡u/')
        self.assertEqual(IPA('/aoua͡ou/', IPAConfig(combined=[('ao', 'u')])), '/ao͡ua͡ou/')

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
            IPASymbol('a').features({'Height'}),  # type: ignore
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
            IPASymbol('a').features({Height, 'HeightCategory'}),  # type: ignore
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

        self.assertEqual(Manner.class_values(), ['Manner', 'manner'])
        self.assertEqual(SymbolType.class_values(), ['SymbolType', 'symbol type'])
        self.assertEqual(Feature.class_values(), [])

        with self.assertRaises(FeatureKindError) as context:
            IPASymbol('a').features({Airflow, unknown, Voicing})  # type: ignore
        self.assertEqual(context.exception.value, unknown)

        with self.assertRaises(FeatureError) as context:
            IPASymbol('a').features(role=unknown)  # type: ignore
        self.assertEqual(context.exception.value, unknown)

    def test_representation(self) -> None:
        self.assertEqual(str(IPA('/abc/')), IPA('/abc/').as_string(), '/abc/')
        self.assertEqual(repr(IPA('[abc]')), "IPA('[abc]')")
        self.assertEqual(str(IPASymbol('ts')), IPASymbol('ts').as_string(), 'ts')
        self.assertEqual(repr(IPASymbol('ts')), "IPASymbol('ts')")

    def test_equality(self) -> None:
        self.assertEqual(IPA('[abc]'), IPA('[abc]'))
        self.assertEqual(IPA('[abc]'), '[abc]')
        self.assertEqual('[abc]', IPA('[abc]'))
        self.assertNotEqual(IPA('[abc]'), IPA('/abc/'))
        self.assertNotEqual(IPA('/abc/'), '[abc]')
        self.assertNotEqual(IPA('[abc]'), IPA('[abd]'))
        self.assertNotEqual(IPA('/a/'), IPASymbol('a'))
        self.assertNotEqual(IPASymbol('a'), IPA('[a]'))

    def test_operations(self) -> None:
        transcriptions = set()
        transcriptions.add(IPA('[abc]'))
        transcriptions.add(IPA('[def]'))
        transcriptions.add(IPA('/abc/'))
        transcriptions.add(IPA('[ghi]'))
        transcriptions.add(IPA('[abc]'))
        transcriptions.add(IPA('[cba]'))
        self.assertEqual(len(transcriptions), 5)

        self.assertTrue(isinstance(IPA('/abc/') + IPA('/def/'), IPA))
        self.assertEqual(to_features(IPA('[abc]')) + to_features(IPA('[Vef]')), to_features(IPA('[abcVef]')))
        self.assertEqual(IPA('/abc/') + IPA('/def/'), '/abcdef/')
        self.assertEqual(IPA('[abc]') + IPA('[def]'), '[abcdef]')
        self.assertEqual(IPA('[abc]') + IPASymbol('d'), '[abcd]')
        self.assertEqual(IPASymbol('a') + IPA('/bcd/'), '/abcd/')
        with self.assertRaises(IncompatibleTypesError):
            IPA('/a/') + IPA('[b]')
        with self.assertRaises(TypeError):
            IPA('[a]') + '[b]'
        with self.assertRaises(TypeError):
            IPA('/a/') + 'b'
        with self.assertRaises(TypeError):
            3 + IPA('[a]')

        self.assertTrue(isinstance(IPA('[abc]') * 4, IPA))
        self.assertEqual(IPA('[abc]') * 4, 4 * IPA('[abc]'), '[abcabcabcabc]')
        self.assertEqual(IPA('/abc/') * 0, 0 * IPA('/abc/'), '//')
        with self.assertRaises(TypeError):
            IPA('[abc]') * 4.0
        with self.assertRaises(TypeError):
            'abc' * IPA('/abc/')

        self.assertEqual(list(IPA('[abct͡s]')), ['a', 'b', 'c', 't͡s'])
        self.assertEqual(len(IPA('/abct͡s/')), 4)
        self.assertEqual(len(IPA('⟨⟩')), 0)
        self.assertTrue(isinstance(IPA('[abct͡s]')[0], IPASymbol))
        self.assertTrue(isinstance(IPA('/abct͡s/')[-1], IPASymbol))
        self.assertTrue(isinstance(IPA('/abct͡s/')[1:2], IPA))
        self.assertEqual(IPA('[abct͡s]')[0], 'a')
        self.assertEqual(IPA('[abct͡s]')[2], 'c')
        self.assertEqual(IPA('/abct͡s/')[-1], 't͡s')
        self.assertEqual(IPA('/abct͡sz/')[2:4], '/ct͡s/')
        self.assertEqual(IPA('/abct͡sz/')[:], '/abct͡sz/')
        self.assertEqual(IPA('[abct͡sz]')[100:0], '[]')
        with self.assertRaises(IndexError):
            self.assertEqual(IPA('[abc]')[10], None)
        with self.assertRaises(TypeError):
            self.assertEqual(IPA('[abc]')['a'], None)  # type: ignore
