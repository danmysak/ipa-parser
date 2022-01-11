from .feature import Feature

__all__ = [
    'Roundedness',
    'RoundednessModifier',
]


class Roundedness(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Vowels
    """

    ROUNDED = 'rounded'


class RoundednessModifier(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation
    https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet#Diacritics
    """

    MORE_ROUNDED = 'more rounded'
    LESS_ROUNDED = 'less rounded'
    COMPRESSED = 'compressed'
    LABIAL_SPREADING = 'labial spreading'
