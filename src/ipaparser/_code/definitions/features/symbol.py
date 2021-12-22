from .feature import Feature

__all__ = [
    'SymbolType',
]


class SymbolType(Feature):
    SOUND = 'sound'
    SUPRASEGMENTAL = 'suprasegmental'
    BREAK = 'break'
    UNKNOWN = 'unknown'
