from ..helpers.enums import assert_enum_mapping, StrEnum

__all__ = [
    'SoundSubtype',
    'SoundType',
]


class SoundType(StrEnum):
    CONSONANT = 'consonant'
    VOWEL = 'vowel'


class SoundSubtype(StrEnum):
    SIMPLE_CONSONANT = 'simple consonant'
    AFFRICATE = 'affricate'
    COARTICULATED_CONSONANT = 'coarticulated consonant'
    SIMPLE_VOWEL = 'simple vowel'
    DIPHTHONG = 'diphthong'

    def to_sound_type(self) -> SoundType:
        return SOUND_SUBTYPE_TO_TYPE[self]


SOUND_SUBTYPE_TO_TYPE = assert_enum_mapping({
    SoundSubtype.SIMPLE_CONSONANT: SoundType.CONSONANT,
    SoundSubtype.AFFRICATE: SoundType.CONSONANT,
    SoundSubtype.COARTICULATED_CONSONANT: SoundType.CONSONANT,
    SoundSubtype.SIMPLE_VOWEL: SoundType.VOWEL,
    SoundSubtype.DIPHTHONG: SoundType.VOWEL,
})
