from .feature import Feature

__all__ = [
    'Aspiration',
]


class Aspiration(Feature):
    ASPIRATED = 'aspirated'
    UNASPIRATED = 'unaspirated'
    PREASPIRATED = 'preaspirated'
