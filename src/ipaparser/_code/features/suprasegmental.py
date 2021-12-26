from .feature import Feature

__all__ = [
    'SuprasegmentalType',
]


class SuprasegmentalType(Feature):
    STRESS = 'stress'
    TONE = 'tone'
    INTONATION = 'intonation'
    AIRFLOW = 'airflow'
