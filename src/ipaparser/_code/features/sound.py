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
    AFFRICATE_CONSONANT = 'affricate consonant'
    DOUBLY_ARTICULATED_CONSONANT = 'doubly articulated consonant'
    SIMPLE_VOWEL = 'simple vowel'
    DIPHTHONG_VOWEL = 'diphthong vowel'
    TRIPHTHONG_VOWEL = 'triphthong vowel'

    def to_sound_type(self) -> SoundType:
        return SOUND_SUBTYPE_TO_TYPE[self]


SOUND_SUBTYPE_TO_TYPE = assert_feature_mapping({
    SoundSubtype.SIMPLE_CONSONANT: SoundType.CONSONANT,
    SoundSubtype.AFFRICATE_CONSONANT: SoundType.CONSONANT,
    SoundSubtype.DOUBLY_ARTICULATED_CONSONANT: SoundType.CONSONANT,
    SoundSubtype.SIMPLE_VOWEL: SoundType.VOWEL,
    SoundSubtype.DIPHTHONG_VOWEL: SoundType.VOWEL,
    SoundSubtype.TRIPHTHONG_VOWEL: SoundType.VOWEL,
})