from ..helpers.enums import StrEnum

__all__ = [
    'Aspiration',
]


class Aspiration(StrEnum):
    ASPIRATED = 'aspirated'
    UNASPIRATED = 'unaspirated'
    PREASPIRATED = 'preaspirated'
