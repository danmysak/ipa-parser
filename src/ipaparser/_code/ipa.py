from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterator, Optional, overload, SupportsIndex, Union

from .data import get_data
from .definitions import TranscriptionType
from .exceptions import EnclosingError, IncompatibleTypesError
from .ipa_config import IPAConfig
from .ipa_symbol import from_raw, IPASymbol
from .parser import parse

__all__ = [
    'IPA',
]


@dataclass(frozen=True)
class TypeData:
    type: TranscriptionType
    left_bracket: str
    right_bracket: str


@dataclass(frozen=True)
class ParsedEnclosing:
    type: TypeData
    text: str


def parse_enclosing(string: str) -> Optional[ParsedEnclosing]:
    for (left, right), transcription_type in get_data().outer_brackets.items():
        if (len(string) >= len(left + right)
                and string.startswith(left)
                and string.endswith(right)):
            return ParsedEnclosing(
                type=TypeData(
                    type=transcription_type,
                    left_bracket=left,
                    right_bracket=right,
                ),
                text=string.removeprefix(left).removesuffix(right),
            )
    return None


class IPA:
    """Transcription parser."""

    _type: TypeData

    @property
    def type(self) -> TranscriptionType:
        """Type of the transcription (determined by the enclosing brackets)."""
        return self._type.type

    @property
    def left_bracket(self) -> str:
        """Opening bracket of the transcription."""
        return self._type.left_bracket

    @property
    def right_bracket(self) -> str:
        """Closing bracket of the transcription."""
        return self._type.right_bracket

    _symbols: list[IPASymbol]

    def __str__(self) -> str:
        return f'{self.left_bracket}{"".join(str(symbol) for symbol in self._symbols)}{self.right_bracket}'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({repr(str(self))})'

    def __eq__(self, other: Any) -> bool:
        return str(self) == str(other) if isinstance(other, (IPA, str)) else NotImplemented

    def __hash__(self) -> int:
        return hash(str(self))  # str instead of repr is required to be compatible with __eq__

    def __add__(self, other: Any) -> IPA:
        if isinstance(other, IPA):
            if self._type == other._type:
                return self._from_symbols(self._symbols + other._symbols)
            else:
                raise IncompatibleTypesError(str(self), str(other))
        elif isinstance(other, IPASymbol):
            return self._from_symbols(self._symbols + [other])
        else:
            return NotImplemented

    def __radd__(self, other: Any) -> IPA:
        if isinstance(other, IPASymbol):
            return self._from_symbols([other] + self._symbols)
        else:
            return NotImplemented

    def __mul__(self, other: Any) -> IPA:
        return self._from_symbols(self._symbols * other) if isinstance(other, int) else NotImplemented

    def __rmul__(self, other: Any) -> IPA:
        return self.__mul__(other)

    def __iter__(self) -> Iterator[IPASymbol]:
        return iter(self._symbols)

    def __len__(self) -> int:
        return len(self._symbols)

    @overload
    def __getitem__(self, item: SupportsIndex) -> IPASymbol:
        ...

    @overload
    def __getitem__(self, items: slice) -> IPA:
        ...

    def __getitem__(self, items: Union[SupportsIndex, slice]) -> Union[IPASymbol, IPA]:
        try:
            symbols = self._symbols[items]
        except IndexError:
            raise IndexError(f'Index {items} is out of range for {str(self)}')
        except TypeError:
            raise TypeError(f'Index must be either an integer or a slice, got {repr(items)}')
        return self._from_symbols(symbols) if isinstance(items, slice) else symbols

    def __init__(self, transcription: str, config: IPAConfig = IPAConfig()) -> None:
        """Parse a (properly enclosed) transcription string.

        :param transcription: The string to parse (like '[aɪ pʰiː eɪ]').
        :param config: Parsing parameters.
        :raises:
            EnclosingError: The input string is not properly enclosed in brackets (like [so] or /so/).
        """
        enclosing = parse_enclosing(transcription)
        if not enclosing:
            raise EnclosingError(transcription)
        self._type = enclosing.type
        self._symbols = [from_raw(symbol) for symbol in parse(enclosing.text, config)]

    def as_string(self) -> str:
        """Return the transcription's underlying (normalized) string."""
        return str(self)

    def _from_symbols(self, symbols: list[IPASymbol]) -> IPA:
        ipa = IPA.__new__(IPA)
        ipa._type = self._type
        ipa._symbols = symbols
        return ipa
