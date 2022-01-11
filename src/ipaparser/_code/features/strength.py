from .feature import Feature

__all__ = [
    'Strength',
]


class Strength(Feature):
    """
    https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet#Diacritics
    """

    STRONG = 'strong'
    WEAK = 'weak'
