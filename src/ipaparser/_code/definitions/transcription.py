from ..helpers.enums import StrEnum

__all__ = [
    'TranscriptionType',
]


class TranscriptionType(StrEnum):
    PHONETIC = 'phonetic'
    PHONEMIC = 'phonemic'
