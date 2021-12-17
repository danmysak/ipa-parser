from ..helpers.enums import StrEnum

__all__ = [
    'GraphemeType',
]


class GraphemeType(StrEnum):
    SOUND = 'sound'
    SUPRASEGMENTAL = 'suprasegmental'
    BREAK = 'break'
    UNKNOWN = 'unknown'
