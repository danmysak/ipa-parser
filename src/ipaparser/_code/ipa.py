from dataclasses import dataclass
from operator import attrgetter
from typing import Optional

from .data import get_data
from .definitions import TranscriptionType
from .exceptions import EnclosingError
from .ipa_config import IPAConfig
from .ipa_symbol import IPASymbol, from_raw
from .parser import parse

__all__ = [
    'IPA',
]


@dataclass(frozen=True)
class EnclosingData:
    type: TranscriptionType
    left: str
    right: str
    text: str


def parse_enclosing(string: str) -> Optional[EnclosingData]:
    for (left, right), transcription_type in get_data().outer_brackets.items():
        if (len(string) >= len(left + right)
                and string.startswith(left)
                and string.endswith(right)):
            return EnclosingData(
                type=transcription_type,
                left=left,
                right=right,
                text=string.removeprefix(left).removesuffix(right),
            )
    return None


class IPA:
    """Transcription parser."""

    _type: TranscriptionType
    type: TranscriptionType = property(attrgetter('_type'))

    _left_bracket: str
    left_bracket: str = property(attrgetter('_left_bracket'))

    _right_bracket: str
    right_bracket: str = property(attrgetter('_right_bracket'))

    _symbols: list[IPASymbol]

    def __str__(self) -> str:
        return f'{self._left_bracket}{"".join(str(symbol) for symbol in self._symbols)}{self._right_bracket}'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({repr(str(self))})'

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
        self._left_bracket = enclosing.left
        self._right_bracket = enclosing.right
        self._symbols = [from_raw(symbol.data) for symbol in parse(enclosing.text, config).symbols]
