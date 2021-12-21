from .feature import Feature

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
