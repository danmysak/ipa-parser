from .feature import assert_feature_mapping, Feature
from .symbol import SymbolType

__all__ = [
    'SoundSubtype',
    'SoundType',
]


class SoundType(Feature):
    CONSONANT = 'consonant'
    VOWEL = 'vowel'

    def derived(self) -> SymbolType:
        return SymbolType.SOUND


class SoundSubtype(Feature):
    SIMPLE_CONSONANT = 'simple consonant'
    DOUBLY_ARTICULATED_CONSONANT = 'doubly articulated consonant'
    SIMPLE_VOWEL = 'simple vowel'
    DIPHTHONG_VOWEL = 'diphthong vowel'
    TRIPHTHONG_VOWEL = 'triphthong vowel'

    def derived(self) -> SoundType:
        return SOUND_SUBTYPE_TO_TYPE[self]


SOUND_SUBTYPE_TO_TYPE = assert_feature_mapping({
    SoundSubtype.SIMPLE_CONSONANT: SoundType.CONSONANT,
    SoundSubtype.DOUBLY_ARTICULATED_CONSONANT: SoundType.CONSONANT,
    SoundSubtype.SIMPLE_VOWEL: SoundType.VOWEL,
    SoundSubtype.DIPHTHONG_VOWEL: SoundType.VOWEL,
    SoundSubtype.TRIPHTHONG_VOWEL: SoundType.VOWEL,
})
