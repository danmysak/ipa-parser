from typing import Iterable, Optional

from .definitions.brackets import BracketStrategy
from .ipa import IPA

__all__ = [
    'parse_ipa',
]


def parse_ipa(
        transcription: str, *,
        substitutions: bool = True,
        brackets: BracketStrategy = BracketStrategy.EXPAND,
        combine: Optional[Iterable[tuple[str, str]]] = None,
) -> IPA:
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
        TranscriptionEnclosingError: The input string is not properly enclosed in brackets (like [so] or /so/);
                                     or the first character after the opening bracket is combining (as in /̃here/);
                                     or a tie extends to the closing bracket (as in /here͜/).
    """
    pass
