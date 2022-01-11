from .feature import Feature
from .suprasegmental import SuprasegmentalType

__all__ = [
    'Intonation',
]


class Intonation(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals
    """

    GLOBAL_RISE = 'global rise'
    GLOBAL_FALL = 'global fall'

    def derived(self) -> SuprasegmentalType:
        return SuprasegmentalType.INTONATION
