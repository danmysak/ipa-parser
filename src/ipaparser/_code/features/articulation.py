from .feature import Feature

__all__ = [
    'Articulation',
]


class Articulation(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation
    """

    APICAL = 'apical'
    LAMINAL = 'laminal'
    ADVANCED = 'advanced'
    RETRACTED = 'retracted'
    CENTRALIZED = 'centralized'
    MID_CENTRALIZED = 'mid-centralized'
    RAISED = 'raised'
    LOWERED = 'lowered'
