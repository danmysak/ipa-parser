import unicodedata

__all__ = [
    'decompose',
    'is_decomposed',
    'upper_camel_to_spaces',
]

DECOMPOSED_FORM = 'NFD'


def decompose(string: str) -> str:
    return unicodedata.normalize(DECOMPOSED_FORM, string)


def is_decomposed(string: str) -> bool:
    return unicodedata.is_normalized(DECOMPOSED_FORM, string)


def upper_camel_to_spaces(string: str) -> str:
    result: list[str] = []
    for index, character in enumerate(string):
        if character.isupper():
            if index > 0:
                result.append(' ')
            result.append(character.lower())
        else:
            result.append(character)
    return ''.join(result)
