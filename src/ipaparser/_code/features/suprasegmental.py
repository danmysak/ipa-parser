from .feature import Feature
from .symbol import SymbolType

__all__ = [
    'SuprasegmentalType',
]


class SuprasegmentalType(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals
    https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet#Diacritics
    """

    STRESS = 'stress'
    TONE = 'tone'
    INTONATION = 'intonation'
    AIRFLOW = 'airflow'

    def derived(self) -> SymbolType:
        return SymbolType.SUPRASEGMENTAL
