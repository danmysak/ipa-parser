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
    """
    https://en.wikipedia.org/wiki/Doubly_articulated_consonant
    https://en.wikipedia.org/wiki/Pulmonic-contour_click
    https://en.wikipedia.org/wiki/Ejective-contour_click
    https://en.wikipedia.org/wiki/Diphthong
    https://en.wikipedia.org/wiki/Triphthong
    """

    SIMPLE_CONSONANT = 'simple consonant'
    DOUBLY_ARTICULATED_CONSONANT = 'doubly articulated consonant'
    CONTOUR_CLICK = 'contour click'
    SIMPLE_VOWEL = 'simple vowel'
    DIPHTHONG = 'diphthong'
    TRIPHTHONG = 'triphthong'

    def derived(self) -> SoundType:
        return SOUND_SUBTYPE_TO_TYPE[self]


SOUND_SUBTYPE_TO_TYPE = assert_feature_mapping({
    SoundSubtype.SIMPLE_CONSONANT: SoundType.CONSONANT,
    SoundSubtype.DOUBLY_ARTICULATED_CONSONANT: SoundType.CONSONANT,
    SoundSubtype.CONTOUR_CLICK: SoundType.CONSONANT,
    SoundSubtype.SIMPLE_VOWEL: SoundType.VOWEL,
    SoundSubtype.DIPHTHONG: SoundType.VOWEL,
    SoundSubtype.TRIPHTHONG: SoundType.VOWEL,
})
