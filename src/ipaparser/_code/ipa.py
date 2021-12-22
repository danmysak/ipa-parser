from __future__ import annotations
from typing import Iterable, Optional

from .definitions.brackets import BracketStrategy

__all__ = [
    'IPA',
    'TranscriptionEnclosingError',
]


class TranscriptionEnclosingError(ValueError):
    pass


class IPA:
    def __init__(
            self, transcription: str, *,
            substitutions: bool = True,
            brackets: BracketStrategy = BracketStrategy.EXPAND,
            combine: Optional[Iterable[tuple[str, str]]] = None,
    ):
        """Parse a (properly enclosed) transcription string into an IPA object.

        :param transcription: The string to parse (like '[aɪ pʰiː eɪ]').
        :param substitutions: Whether to perform normalizing substitutions such as ':' > 'ː' and 'g' > 'ɡ'.
        :param brackets: What to do with brackets in transcriptions denoting optional pronunciation, such as in
                         '[bə(j)ɪz⁽ʲ⁾ˈlʲivɨj]': expand ('[bəjɪzʲˈlʲivɨj]') or strip ('[bəɪzˈlʲivɨj]').
        :param combine: Two-sound sequences to be treated like they are always connected by a tie, e.g.,
                        [('a', 'ɪ'), ('o', 'ʊ̯'), ('t', 's'), ('d̠', 'ɹ̠˔')]; note that, e.g., ('a', 'ɪ') will not match
                        'aɪ̯', and likewise ('a', 'ɪ̯') will not match 'aɪ'.
        :return: An IPA object corresponding to the (normalized) input string.
        :raises:
            TranscriptionEnclosingError: The input string is not properly enclosed in brackets (like [so] or /so/).
        """
        pass
