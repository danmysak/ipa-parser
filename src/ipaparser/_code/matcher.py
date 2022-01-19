from dataclasses import dataclass
from typing import Any, Callable, Generic, Iterable, Optional, TypeVar

from .strings import StringPosition, StringPositions, to_string

__all__ = [
    'Match',
    'Matcher',
    'MatchOption',
]

T = TypeVar('T')


@dataclass(frozen=True)
class MatchOption(Generic[T]):
    data: T
    combining: list[list[str]]


@dataclass(frozen=True)
class Match(Generic[T]):
    length: int
    options: list[MatchOption[T]]

    @property
    def primary_option(self) -> MatchOption[T]:
        return self.options[0]


class Matcher(Generic[T]):
    _max_length: int
    _mapping: dict[str, list[tuple[StringPositions, T]]]
    _option_sorting_key: Callable[[MatchOption[T]], Any]

    def __init__(self, data: Iterable[tuple[StringPositions, T]],
                 option_sorting_key: Callable[[MatchOption[T]], Any]) -> None:
        self._max_length = 0
        self._mapping = {}
        for positions, value in data:
            self._max_length = max(self._max_length, len(positions))
            key = to_string(positions, combining=False)
            if key not in self._mapping:
                self._mapping[key] = []
            self._mapping[key].append((positions, value))
        self._option_sorting_key = option_sorting_key

    @staticmethod
    def _match_with_combining_single(given: StringPosition, required: StringPosition) -> Optional[list[str]]:
        combining: list[str] = []
        required_index = 0
        for character in given:
            if required_index < len(required) and required[required_index] == character:
                required_index += 1
            else:
                combining.append(character)
        return combining if required_index == len(required) else None

    @staticmethod
    def _match_with_combining(given: StringPositions, required: StringPositions) -> Optional[list[list[str]]]:
        assert len(given) == len(required)
        combining: list[list[str]] = []
        for given_position, required_position in zip(given, required):
            combining_single = Matcher._match_with_combining_single(given_position, required_position)
            if combining_single is None:
                return None
            combining.append(combining_single)
        return combining

    def match(self, positions: StringPositions, start: int, length: Optional[int] = None) -> Optional[Match[T]]:
        for match_length in range(min(self._max_length, len(positions) - start), 0, -1) if length is None else [length]:
            given = positions[start:start + match_length]
            if options := [MatchOption(data, combining)
                           for matched, data in self._mapping.get(to_string(given, combining=False), [])
                           if (combining := Matcher._match_with_combining(given, matched)) is not None]:
                return Match(match_length, sorted(options, key=self._option_sorting_key))
        return None
