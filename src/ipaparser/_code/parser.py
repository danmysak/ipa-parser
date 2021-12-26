from dataclasses import dataclass
from typing import Iterator, Optional
import unicodedata

from .data import Combining, get_data, Position
from .decomposer import decompose
from .definitions import BracketStrategy
from .features import Feature
from .ipa_config import IPAConfig
from .ipa_data import IPAData
from .matcher import Match
from .phonetics import apply_combining, basic_symbol_to_features, combine_features, get_basic_matcher, unknown

__all__ = [
    'parse',
    'ParsedData',
    'ParsedSymbol',
]


@dataclass(frozen=True)
class ParsedSymbol:
    data: IPAData
    components: Optional[list[IPAData]]
    is_last: bool


@dataclass(frozen=True)
class ParsedData:
    normalized: str
    symbols: Iterator[ParsedSymbol]


@dataclass(frozen=True)
class BracketData:
    bracket: str
    position: int


@dataclass(frozen=True)
class Chunk:
    match: Optional[Match]
    start: int
    end: int


def perform_substitutions(text: str) -> str:
    for substring, substitution in get_data().substitutions:
        text = text.replace(substring, substitution)
    return text


def expand_brackets(text: str) -> str:
    for left, right in get_data().inner_brackets:
        text = text.replace(left, '').replace(right, '')
    return text


def strip_brackets(text: str) -> str:
    bracket_pairs = set(get_data().inner_brackets)
    opening = {bracket for bracket, _ in bracket_pairs}
    closing = {bracket for _, bracket in bracket_pairs}
    open_deltas = [0 for _ in text]
    currently_open: list[BracketData] = []
    for position, character in enumerate(text):
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
    for character, delta in zip(text, open_deltas):
        open_count += delta
        if open_count == 0:
            taken.append(character)
    return ''.join(taken)


def combine_single(text: str, sequence: tuple[str, ...]) -> str:
    if len(sequence) <= 1:
        raise ValueError(f'Attempt to combine a sequence of length {len(sequence)}')
    substring = ''.join(sequence)
    sections: list[str] = []
    position = 0

    def advance(next_position: int) -> None:
        nonlocal position
        sections.append(text[position:next_position])
        position = next_position

    while (occurrence := text.find(substring, position)) >= 0:
        following_position = occurrence + len(substring)
        if following_position < len(text) and unicodedata.combining(text[following_position]):
            advance(occurrence + 1)
            continue
        for index, sound in enumerate(sequence):
            if not sound:
                raise ValueError('Attempt to combine a sequence containing an empty sound')
            if index > 0:
                sections.append(get_data().main_tie)
            advance(position + len(sound))
    advance(len(text))
    return ''.join(sections)


def combine(text: str, combined: tuple[tuple[str, ...]]) -> str:
    for sequence in combined:
        text = combine_single(text, sequence)
    return text


def get_unmatched_tied_chunk_end(text: str, start: int) -> int:
    if start == len(text):
        raise ValueError('Cannot obtain a chunk: cursor is already at the end of a string')
    ties = get_data().ties
    tied = False
    position = start
    while True:
        if text[position] in ties:
            tied = True
        position += 1
        if position == len(text):
            break
        if not unicodedata.combining(text[position]):
            if tied:
                tied = False
            else:
                break
    return position


def get_tied_chunks(text: str, start: int) -> Iterator[Chunk]:
    ties = get_data().ties
    position = start
    while True:
        if position == len(text):
            yield Chunk(  # So that a tie at the end of the string is not left unnoticed
                match=None,
                start=position,
                end=position,
            )
            return
        if match := get_basic_matcher().match(text, position):
            next_position = position + match.total_length()
            yield Chunk(
                match=match,
                start=position,
                end=next_position,
            )
            position = next_position
            assert match.extra_diacritics_by_position
            if ties.isdisjoint(match.extra_diacritics_by_position[-1]):
                return
        else:
            yield Chunk(
                match=None,
                start=position,
                end=get_unmatched_tied_chunk_end(text, position),
            )
            return


def match_to_features(match: Match, *, ignore_closing_ties: bool) -> Optional[set[Feature]]:
    features = basic_symbol_to_features(match.string)
    if features is None:
        return None
    applied: set[Combining] = set()
    for index, position in enumerate(match.extra_diacritics_by_position):
        ignored_diacritics = (
            get_data().ties
            if ignore_closing_ties and index == len(match.extra_diacritics_by_position) - 1
            else set()
        )
        for diacritic in position:
            if diacritic in ignored_diacritics:
                continue
            combining = Combining(
                character=diacritic,
                position=Position.FOLLOWING,
            )
            if combining not in applied:
                features = apply_combining(combining, features)
                if features is None:
                    return None
                applied.add(combining)
    return features


def tied_matches_to_features(matches: list[Match]) -> Optional[tuple[set[Feature], Optional[list[set[Feature]]]]]:
    if not matches:
        raise ValueError('Attempt to map empty matches to features')
    feature_sets: list[set[Feature]] = []
    for index, match in enumerate(matches):
        is_last_match = index == len(matches) - 1
        features = match_to_features(match, ignore_closing_ties=not is_last_match)
        if features is None:
            return None
        feature_sets.append(features)
    if len(feature_sets) > 1:
        return (combined, feature_sets) if (combined := combine_features(feature_sets)) is not None else None
    else:
        return feature_sets[0], None


def parse_normalized(text: str) -> Iterator[ParsedSymbol]:
    hanging: list[str] = []

    def dump_hanging(*, is_last: bool) -> Iterator[ParsedSymbol]:
        if hanging:
            yield ParsedSymbol(
                data=IPAData(string=''.join(hanging), features=unknown()),
                components=None,
                is_last=is_last,
            )
            hanging.clear()

    position = 0
    while position < len(text):
        chunks = list(get_tied_chunks(text, position))
        following_position = chunks[-1].end
        if all(matches := [chunk.match for chunk in chunks]) and (feature_sets := tied_matches_to_features(matches)):
            features, components = feature_sets
            while hanging and len(hanging[-1]) == 1 and (new_features := apply_combining(Combining(
                character=hanging[-1],
                position=Position.PRECEDING,
            ), features)) is not None:
                features = new_features
                hanging.pop()
                position -= 1
            yield from dump_hanging(is_last=False)
            while (following_position < len(text)
                   and get_unmatched_tied_chunk_end(text, following_position) == following_position + 1
                   and (new_features := apply_combining(Combining(
                            character=text[following_position],
                            position=Position.FOLLOWING,
                        ), features)) is not None):
                features = new_features
                following_position += 1
            yield ParsedSymbol(
                data=IPAData(string=text[position:following_position], features=features),
                components=[IPAData(string=text[chunk.start:chunk.end], features=component)
                            for chunk, component in zip(chunks, components)] if components is not None else None,
                is_last=following_position == len(text),
            )
        else:
            hanging.append(text[position:following_position])
        position = following_position
    yield from dump_hanging(is_last=True)


def parse(text: str, config: IPAConfig) -> ParsedData:
    text = decompose(text)
    if config.substitutions:
        text = perform_substitutions(text)
    if config.brackets == BracketStrategy.EXPAND:
        text = expand_brackets(text)
    elif config.brackets == BracketStrategy.STRIP:
        text = strip_brackets(text)
    text = combine(text, config.combined)
    return ParsedData(
        normalized=text,
        symbols=parse_normalized(text),
    )
