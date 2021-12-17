from ..helpers.enums import StrEnum

__all__ = [
    'BracketStrategy',
]


class BracketStrategy(StrEnum):
    EXPAND = 'expand'
    STRIP = 'strip'
