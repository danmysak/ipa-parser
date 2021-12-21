from .feature import Feature

__all__ = [
    'Roundedness',
    'RoundednessModifier',
]


class Roundedness(Feature):
    ROUNDED = 'rounded'


class RoundednessModifier(Feature):
    MORE_ROUNDED = 'more rounded'
    LESS_ROUNDED = 'less rounded'
    COMPRESSED = 'compressed'
    LABIAL_SPREADING = 'labial spreading'
