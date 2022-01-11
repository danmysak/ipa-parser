from .feature import Feature

__all__ = [
    'Aspiration',
]


class Aspiration(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation
    https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet#Diacritics
    """

    ASPIRATED = 'aspirated'
    UNASPIRATED = 'unaspirated'
    PREASPIRATED = 'preaspirated'
