from ...helpers.enums import StrEnum

__all__ = [
    'UnitType',
]


class UnitType(StrEnum):
    SOUND = 'sound'
    SUPRASEGMENTAL = 'suprasegmental'
    BREAK = 'break'
    UNKNOWN = 'unknown'
