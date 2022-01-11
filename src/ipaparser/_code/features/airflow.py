from .feature import Feature
from .suprasegmental import SuprasegmentalType

__all__ = [
    'Airflow',
]


class Airflow(Feature):
    """
    https://en.wikipedia.org/wiki/Extensions_to_the_International_Phonetic_Alphabet#Diacritics
    """

    EGRESSIVE_AIRFLOW = 'egressive airflow'
    INGRESSIVE_AIRFLOW = 'ingressive airflow'

    def derived(self) -> SuprasegmentalType:
        return SuprasegmentalType.AIRFLOW
