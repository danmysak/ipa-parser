from enum import Enum

__all__ = [
    'TranscriptionType',
]


class TranscriptionType(str, Enum):
    PHONETIC = 'phonetic'
    PHONEMIC = 'phonemic'
    LITERAL = 'literal'
