from dataclasses import dataclass
import unicodedata

from .data_types import InnerBracketData, SubstitutionData

__all__ = [
    'combine',
    'decompose',
    'expand_brackets',
    'is_decomposed',
    'perform_substitutions',
    'StringPositions',
    'strip_brackets',
    'to_positions',
    'to_string',
    'upper_camel_to_spaces',
]

DECOMPOSED_FORM = 'NFD'

StringPositions = tuple[str, ...]  # nonempty substrings starting with a non-combining character each


def decompose(string: str) -> str:
    return unicodedata.normalize(DECOMPOSED_FORM, string)


def is_decomposed(string: str) -> bool:
    return unicodedata.is_normalized(DECOMPOSED_FORM, string)


def to_positions(string: str) -> StringPositions:
    start_indices = [index for index in range(len(string)) if index == 0 or not unicodedata.combining(string[index])]
    return tuple(string[start:end] for start, end in zip(start_indices, start_indices[1:] + [len(string)]))


def to_string(positions: StringPositions, *, combining: bool = True) -> str:
    return ''.join((position if combining else position[0]) for position in positions)


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


def perform_substitutions(string: str, substitutions: SubstitutionData) -> str:
    for substring, substitution in substitutions:
        string = string.replace(substring, substitution)
    return string


def expand_brackets(string: str, brackets: InnerBracketData) -> str:
    for left, right in brackets:
        string = string.replace(left, '').replace(right, '')
    return string


@dataclass(frozen=True)
class BracketData:
    bracket: str
    position: int


def strip_brackets(string: str, brackets: InnerBracketData) -> str:
    bracket_pairs = set(brackets)
    opening = {bracket for bracket, _ in bracket_pairs}
    closing = {bracket for _, bracket in bracket_pairs}
    open_deltas = [0 for _ in string]
    currently_open: list[BracketData] = []
    for position, character in enumerate(string):
        if character in opening:
            currently_open.append(BracketData(
                bracket=character,
                position=position,
            ))
        elif character in closing:
            if currently_open and (currently_open[-1].bracket, character) in bracket_pairs:
                matched = currently_open.pop()
                open_deltas[matched.position] = 1
                open_deltas[position] = -1
            else:
                currently_open.clear()  # Not stripping any content unless the brackets are well-balanced
    taken: list[str] = []
    open_count = 0
    for character, delta in zip(string, open_deltas):
        open_count += delta
        if open_count == 0:
            taken.append(character)
    return ''.join(taken)


def combine_single(string: str, sequence: tuple[str, ...], tie: str) -> str:
    if len(sequence) <= 1:
        raise ValueError(f'Attempt to combine a sequence of length {len(sequence)}')
    substring = ''.join(sequence)
    sections: list[str] = []
    position = 0

    def advance(next_position: int) -> None:
        nonlocal position
        sections.append(string[position:next_position])
        position = next_position

    while (occurrence := string.find(substring, position)) >= 0:
        following_position = occurrence + len(substring)
        if following_position < len(string) and unicodedata.combining(string[following_position]):
            advance(occurrence + 1)
            continue
        for index, sound in enumerate(sequence):
            if not sound:
                raise ValueError('Attempt to combine a sequence containing an empty sound')
            if index > 0:
                sections.append(tie)
            advance(position + len(sound))
    advance(len(string))
    return ''.join(sections)


def combine(string: str, combined: tuple[tuple[str, ...]], tie: str) -> str:
    for sequence in combined:
        string = combine_single(string, sequence, tie)
    return string
