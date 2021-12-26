from enum import Enum

__all__ = [
    'BracketStrategy',
]


class BracketStrategy(str, Enum):
    KEEP = 'keep'
    EXPAND = 'expand'
    STRIP = 'strip'
