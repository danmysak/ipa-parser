from .feature import Feature

__all__ = [
    'Manner',
]


class Manner(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Consonants
    """

    AFFRICATE = 'affricate'
    APPROXIMANT = 'approximant'
    FRICATIVE = 'fricative'
    LATERAL = 'lateral'
    NASAL = 'nasal'
    SIBILANT = 'sibilant'
    STOP = 'stop'
    TAP_FLAP = 'tap/flap'
    TRILL = 'trill'

    CLICK = 'click'
    EJECTIVE = 'ejective'
    IMPLOSIVE = 'implosive'
