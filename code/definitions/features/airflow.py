from ...helpers.enums import StrEnum

__all__ = [
    'Airflow',
]


class Airflow(StrEnum):
    EGRESSIVE_AIRFLOW = 'egressive airflow'
    INGRESSIVE_AIRFLOW = 'ingressive airflow'
