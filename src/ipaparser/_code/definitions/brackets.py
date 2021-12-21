from enum import Enum

__all__ = [
    'BracketStrategy',
]


class BracketStrategy(str, Enum):
    EXPAND = 'expand'
    STRIP = 'strip'
