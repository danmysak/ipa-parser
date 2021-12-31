from .feature import Feature
from .symbol import SymbolType

__all__ = [
    'SuprasegmentalType',
]


class SuprasegmentalType(Feature):
    STRESS = 'stress'
    TONE = 'tone'
    INTONATION = 'intonation'
    AIRFLOW = 'airflow'

    def derived(self) -> SymbolType:
        return SymbolType.SUPRASEGMENTAL
