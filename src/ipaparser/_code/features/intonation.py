from .feature import Feature
from .suprasegmental import SuprasegmentalType

__all__ = [
    'Intonation',
]


class Intonation(Feature):
    GLOBAL_RISE = 'global rise'
    GLOBAL_FALL = 'global fall'

    def derived(self) -> SuprasegmentalType:
        return SuprasegmentalType.INTONATION
