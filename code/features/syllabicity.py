from ..helpers.enums import StrEnum

__all__ = [
    'Syllabicity',
]


class Syllabicity(StrEnum):
    SYLLABIC = 'syllabic'
    NONSYLLABIC = 'nonsyllabic'
    ANAPTYCTIC = 'anaptyctic'
