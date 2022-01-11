from .feature import Feature

__all__ = [
    'SecondaryModifier',
    'SecondaryPlace',
]


class SecondaryPlace(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation
    """

    LABIALIZED = 'labialized'
    PALATALIZED = 'palatalized'
    VELARIZED = 'velarized'
    PHARYNGEALIZED = 'pharyngealized'
    GLOTTALIZED = 'glottalized'


class SecondaryModifier(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Diacritics_and_prosodic_notation
    https://en.wikipedia.org/wiki/Prenasalized_consonant
    https://en.wikipedia.org/wiki/Pre-stopped_consonant
    https://linguistics.ucla.edu/people/keating/Keating_JIPA_diacritics_accepted_complete_Feb2019.pdf
    https://en.wikipedia.org/wiki/Glottalized_click#Preglottalized_nasal_clicks
    """

    ADVANCED_TONGUE_ROOT = 'advanced tongue root'
    RETRACTED_TONGUE_ROOT = 'retracted tongue root'
    R_COLORED = 'r-colored'
    NASALIZED = 'nasalized'
    PRENASALIZED = 'prenasalized'
    VOICELESSLY_PRENASALIZED = 'voicelessly prenasalized'
    PRESTOPPED = 'prestopped'
    PREGLOTTALIZED = 'preglottalized'
