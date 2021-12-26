from .feature import Feature

__all__ = [
    'Syllabicity',
]


class Syllabicity(Feature):
    SYLLABIC = 'syllabic'
    NONSYLLABIC = 'nonsyllabic'
    ANAPTYCTIC = 'anaptyctic'
