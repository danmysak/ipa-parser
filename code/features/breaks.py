from ..helpers.enums import StrEnum

__all__ = [
    'BreakType',
]


class BreakType(StrEnum):
    SPACE = 'space'
    HYPHEN = 'hyphen'
    LINKING = 'linking'
    SYLLABLE_BREAK = 'syllable break'
    MINOR_BREAK = 'minor break'
    MAJOR_BREAK = 'major break'
    EQUIVALENCE = 'equivalence'
    ELLIPSIS = 'ellipsis'
