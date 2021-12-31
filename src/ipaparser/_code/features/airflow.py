from .feature import Feature
from .suprasegmental import SuprasegmentalType

__all__ = [
    'Airflow',
]


class Airflow(Feature):
    EGRESSIVE_AIRFLOW = 'egressive airflow'
    INGRESSIVE_AIRFLOW = 'ingressive airflow'

    def derived(self) -> SuprasegmentalType:
        return SuprasegmentalType.AIRFLOW
