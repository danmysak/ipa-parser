from unittest import main, TestCase

from ..ipaparser import IPA, IPAConfig
from ..ipaparser.definitions import BracketStrategy, TranscriptionType


class TestApi(TestCase):
    def test_transcription_types(self) -> None:
        self.assertEqual(IPA('[a]').type, TranscriptionType.PHONETIC)
        self.assertEqual(IPA('/a/').type, TranscriptionType.PHONEMIC)
        self.assertEqual(IPA('⟨a⟩').type, TranscriptionType.LITERAL)

    def test_bracket_strategies(self) -> None:
        string = '[(a)bc((d)e)fg⁽ʰ⁾i(j)]'
        self.assertEqual(str(IPA(string, IPAConfig(brackets=BracketStrategy.KEEP))), string)
        self.assertEqual(str(IPA(string, IPAConfig(brackets=BracketStrategy.EXPAND))), '[abcdefgʰij]')
        self.assertEqual(str(IPA(string, IPAConfig(brackets=BracketStrategy.STRIP))), '[bcfgi]')


main()
