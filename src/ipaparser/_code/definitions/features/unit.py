from .feature import Feature

__all__ = [
    'UnitType',
]


class UnitType(Feature):
    SOUND = 'sound'
    SUPRASEGMENTAL = 'suprasegmental'
    BREAK = 'break'
    UNKNOWN = 'unknown'
