from typing import Iterable, Optional

from .definitions.brackets import BracketStrategy
from .ipa import IPA

__all__ = [
    'InvalidCombinationError',
    'parse_ipa',
    'TranscriptionEnclosingError',
]


class TranscriptionEnclosingError(ValueError):
    pass


class InvalidCombinationError(ValueError):
    combination: str

    def __init__(self, message: str, combination: str):
        super().__init__(message)
        self.combination = combination


def parse_ipa(
        transcription: str, *,
        substitutions: bool = True,
        brackets: BracketStrategy = BracketStrategy.EXPAND,
        combine: Optional[Iterable[str]] = None,
) -> IPA:
    """Parse a (properly enclosed) transcription string into an IPA object.

    :param transcription: The string to parse (like '[aɪ pʰiː eɪ]').
    :param substitutions: Whether to perform normalizing substitutions such as ':' > 'ː' and 'g' > 'ɡ'.
    :param brackets: What to do with brackets in transcriptions denoting optional pronunciation, such as in
                     '[bə(j)ɪz⁽ʲ⁾ˈlʲivɨj]': expand ('[bəjɪzʲˈlʲivɨj]', default) or strip ('[bəɪzˈlʲivɨj]').
    :param combine: Two-sound sequences to be treated like they are always connected by a tie, e.g., ['aɪ', 'oʊ̯', 'ts']
                    (note that passing 'aɪ' will also match 'aɪ̯', passing 'ts' will also match 't̪s̪', etc., but
                    _not_ the other way around). Each item must be a valid sound combination: either a diphthong,
                    an affricate, or a co-articulated consonant.
    :return: An IPA object corresponding to the (normalized) input string.
    :raises:
        TranscriptionEnclosingError: The input string is not properly enclosed in brackets (like [so] or /so/);
                                     or the first character after the opening bracket is combining (as in /̃here/);
                                     or a tie extends to the closing bracket (as in /here͜/).
        InvalidCombinationError: One of the sequences provided in the `combine` parameter cannot be interpreted as
                                 either a diphthong, an affricate, or a co-articulated consonant.
    """
    pass
