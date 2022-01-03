from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

from .strings import StringPositions, to_string

__all__ = [
    'Match',
    'Matcher',
]

T = TypeVar('T')


@dataclass(frozen=True)
class Match(Generic[T]):
    length: int
    data: T
    extra: list[str]


class Matcher(Generic[T]):
    _max_length: int
    _mapping: dict[str, list[tuple[StringPositions, T]]]

    def __init__(self, strings: dict[StringPositions, T]) -> None:
        self._max_length = 0
        self._mapping = {}
        for positions, value in strings.items():
            self._max_length = max(self._max_length, len(positions))
            key = to_string(positions, combining=False)
            if key not in self._mapping:
                self._mapping[key] = []
            self._mapping[key].append((positions, value))
        for values in self._mapping.values():
            values.sort(key=lambda option: len(to_string(option[0])), reverse=True)

    @staticmethod
    def _match_with_extra_single(given_position: str, required_position: str) -> Optional[list[str]]:
        extra: list[str] = []
        required_index = 0
        for character in given_position:
            if required_index < len(required_position) and required_position[required_index] == character:
                required_index += 1
            else:
                extra.append(character)
        return extra if required_index == len(required_position) else None

    @staticmethod
    def _match_with_extra(given: StringPositions, required: StringPositions) -> Optional[list[str]]:
        if len(given) != len(required):
            return None
        extra: list[str] = []
        for given_position, required_position in zip(given, required):
            extra_single = Matcher._match_with_extra_single(given_position, required_position)
            if extra_single is None:
                return None
            extra.extend(extra_single)
        return extra

    def match(self, positions: StringPositions, start: int) -> Optional[Match[T]]:
        for length in range(min(self._max_length, len(positions) - start), 0, -1):
            given = positions[start:start + length]
            for required, data in self._mapping.get(to_string(given, combining=False), []):
                if (extra := Matcher._match_with_extra(given, required)) is not None:
                    return Match(length, data, extra)
        return None
