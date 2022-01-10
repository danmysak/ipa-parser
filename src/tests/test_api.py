from unittest import main, TestCase

from ..ipaparser import IPA
from ..ipaparser.definitions import TranscriptionType


class TestApi(TestCase):
    def test_transcription_types(self) -> None:
        self.assertEqual(IPA('[a]').type, TranscriptionType.PHONETIC)
        self.assertEqual(IPA('/a/').type, TranscriptionType.PHONEMIC)
        self.assertEqual(IPA('⟨a⟩').type, TranscriptionType.LITERAL)


main()
