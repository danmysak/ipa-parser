from ..helpers.enums import StrEnum

__all__ = [
    'Intonation',
]


class Intonation(StrEnum):
    GLOBAL_RISE = 'global rise'
    GLOBAL_FALL = 'global fall'
