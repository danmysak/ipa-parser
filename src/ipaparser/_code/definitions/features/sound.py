from .feature import assert_feature_mapping, Feature

__all__ = [
    'SoundSubtype',
    'SoundType',
]


class SoundType(Feature):
    CONSONANT = 'consonant'
    VOWEL = 'vowel'


class SoundSubtype(Feature):
    SIMPLE_CONSONANT = 'simple consonant'
    AFFRICATE = 'affricate'
    DOUBLE_CONSONANT = 'double consonant'
    SIMPLE_VOWEL = 'simple vowel'
    DIPHTHONG = 'diphthong'

    def to_sound_type(self) -> SoundType:
        return SOUND_SUBTYPE_TO_TYPE[self]


SOUND_SUBTYPE_TO_TYPE = assert_feature_mapping({
    SoundSubtype.SIMPLE_CONSONANT: SoundType.CONSONANT,
    SoundSubtype.AFFRICATE: SoundType.CONSONANT,
    SoundSubtype.DOUBLE_CONSONANT: SoundType.CONSONANT,
    SoundSubtype.SIMPLE_VOWEL: SoundType.VOWEL,
    SoundSubtype.DIPHTHONG: SoundType.VOWEL,
})
