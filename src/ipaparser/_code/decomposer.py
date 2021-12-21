import unicodedata

__all__ = [
    'decompose',
    'is_decomposed',
]


def decompose(string: str) -> str:
    return unicodedata.normalize('NFD', string)


def is_decomposed(string: str) -> bool:
    return string == decompose(string)
