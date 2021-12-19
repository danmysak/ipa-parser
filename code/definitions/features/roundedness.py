from ...helpers.enums import StrEnum

__all__ = [
    'Roundedness',
    'RoundednessModifier',
]


class Roundedness(StrEnum):
    ROUNDED = 'rounded'


class RoundednessModifier(StrEnum):
    MORE_ROUNDED = 'more rounded'
    LESS_ROUNDED = 'less rounded'
    COMPRESSED = 'compressed'
    LABIAL_SPREADING = 'labial spreading'
