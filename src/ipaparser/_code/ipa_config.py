from dataclasses import dataclass
from typing import Any, Iterable, Optional, Union
import unicodedata

from .definitions import BracketStrategy
from .exceptions import BracketStrategyError, CombinedLengthError, CombinedSoundError
from .strings import decompose

__all__ = [
    'IPAConfig',
]


def process_substitutions(substitutions: Any) -> bool:
    return bool(substitutions)


def process_brackets(brackets: Union[BracketStrategy, str]) -> BracketStrategy:
    try:
        return BracketStrategy(brackets)
    except ValueError:
        raise BracketStrategyError(brackets, list(BracketStrategy))


def process_combined(combined: Optional[Iterable[tuple[str, ...]]]) -> tuple[tuple[str, ...]]:
    result: list[tuple[str, ...]] = []
    for sequence in combined or []:
        if len(sequence) < 2:
            raise CombinedLengthError(sequence)
        current: list[str] = []
        for sound in sequence:
            if not sound or unicodedata.combining(sound[0]):
                raise CombinedSoundError(sound)
            current.append(decompose(sound))
        result.append(tuple(current))
    return tuple(result)


@dataclass(frozen=True, init=False)
class IPAConfig:
    """Parameter holder for how IPA transcriptions and symbols are parsed."""

    substitutions: bool
    brackets: BracketStrategy
    combined: tuple[tuple[str, ...]]

    def __init__(
            self, *,
            substitutions: bool = False,
            brackets: BracketStrategy = BracketStrategy.KEEP,
            combined: Optional[Iterable[tuple[str, ...]]] = None,
    ) -> None:
        """Set parameters for how IPA transcriptions and symbols are parsed.

        :param substitutions: Whether to perform normalizing substitutions such as ':' > 'ː' and 'g' > 'ɡ'.
        :param brackets: What to do with content in brackets denoting optional pronunciation, such as in
                         [bə(j)ɪz⁽ʲ⁾ˈlʲivɨj]:
                         - keep (and treat brackets as invalid IPA characters),
                         - expand: [bəjɪzʲˈlʲivɨj],
                         - strip: [bəɪzˈlʲivɨj].
        :param combined: Sound sequences to be treated as though they were connected by a tie, for instance,
                         [('t', 's'), ('d̠', 'ɹ̠˔'), ('a', 'ɪ'), ('u̯', 'e', 'i̯')];
                         note that, e.g., ('a', 'ɪ') will not match 'aɪ̯', and likewise ('a', 'ɪ̯') will not match 'aɪ'.
        :raises:
            BracketStrategyError: The `brackets` parameter is a string which does not name a valid strategy.
            CombinedLengthError: Some sequences in the `combined` parameter contain less than two elements.
            CombinedSoundError: Some sounds in the `combined` parameter are empty or start with a combining character.
        """
        object.__setattr__(self, 'substitutions', process_substitutions(substitutions))
        object.__setattr__(self, 'brackets', process_brackets(brackets))
        object.__setattr__(self, 'combined', process_combined(combined))
