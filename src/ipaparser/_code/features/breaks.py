from .feature import Feature
from .symbol import SymbolType

__all__ = [
    'BreakType',
]


class BreakType(Feature):
    SPACE = 'space'
    HYPHEN = 'hyphen'
    LINKING = 'linking'
    SYLLABLE_BREAK = 'syllable break'
    MINOR_BREAK = 'minor break'
    MAJOR_BREAK = 'major break'
    EQUIVALENCE = 'equivalence'
    ELLIPSIS = 'ellipsis'

    def derived(self) -> SymbolType:
        return SymbolType.BREAK
