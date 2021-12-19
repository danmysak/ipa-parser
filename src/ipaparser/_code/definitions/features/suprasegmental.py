from ...helpers.enums import StrEnum

__all__ = [
    'SuprasegmentalType',
]


class SuprasegmentalType(StrEnum):
    STRESS = 'stress'
    TONE = 'tone'
    INTONATION = 'intonation'
    AIRFLOW = 'airflow'
