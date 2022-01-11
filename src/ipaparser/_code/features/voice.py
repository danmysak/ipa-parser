from .feature import Feature

__all__ = [
    'Phonation',
    'Voicing',
]


class Voicing(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Consonants
    https://en.wikipedia.org/wiki/Voicelessness#Voiceless_vowels_and_other_sonorants
    """

    VOICED = 'voiced'
    DEVOICED = 'devoiced'


class Phonation(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation
    https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet#Diacritics
    """

    BREATHY = 'breathy'
    CREAKY = 'creaky'
    WHISPERY = 'whispery'
