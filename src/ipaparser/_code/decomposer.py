import unicodedata

__all__ = [
    'decompose',
    'is_decomposed',
]

FORM = 'NFD'


def decompose(string: str) -> str:
    return unicodedata.normalize(FORM, string)


def is_decomposed(string: str) -> bool:
    return unicodedata.is_normalized(FORM, string)
