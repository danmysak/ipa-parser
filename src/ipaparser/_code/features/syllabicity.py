from .feature import Feature

__all__ = [
    'Syllabicity',
]


class Syllabicity(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation
    https://en.wiktionary.org/wiki/%E1%B5%8A
    """

    SYLLABIC = 'syllabic'
    NONSYLLABIC = 'nonsyllabic'
    ANAPTYCTIC = 'anaptyctic'
