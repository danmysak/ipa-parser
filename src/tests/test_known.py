from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional
from unittest import TestCase

from ..ipaparser import IPA, IPAConfig, IPASymbol

DIRECTORY = Path(__file__).parent
DATA = DIRECTORY / 'known'
TRANSCRIPTIONS = DATA / 'transcriptions'
SYMBOLS = DATA / 'symbols'
SUBSTITUTIONS = DATA / 'substitutions'

COLUMN_DELIMITER = '\t'
VALUE_DELIMITER = ', '
NO_DATA = '—'


@dataclass(frozen=True)
class Symbol:
    symbol: str
    components: Optional[list[str]]
    features: Optional[list[str]]


@dataclass(frozen=True)
class Transcription:
    transcription: str
    symbols: list[str]


@dataclass(frozen=True)
class Substitution:
    original: str
    result: str


RawData = Iterator[tuple[str, tuple[Optional[list[str]], ...]]]


def load_data(path: Path) -> RawData:
    with open(path, 'r') as data:
        for unstripped in data:
            line = unstripped.rstrip('\n')
            item, *columns = line.split(COLUMN_DELIMITER)
            yield item, tuple(map(lambda column: column.split(VALUE_DELIMITER) if column != NO_DATA else None, columns))


def load_transcriptions() -> Iterator[Transcription]:
    for transcription, data in load_data(TRANSCRIPTIONS):
        assert len(data) == 1
        symbols, = data
        assert symbols is not None
        yield Transcription(transcription, symbols)


def load_symbols() -> Iterator[Symbol]:
    for symbol, data in load_data(SYMBOLS):
        assert len(data) == 2
        components, features = data
        yield Symbol(symbol, components, features)


def load_substitutions() -> Iterator[Substitution]:
    for original, data in load_data(SUBSTITUTIONS):
        assert len(data) == 1
        results, = data
        assert len(results) == 1
        result, = results
        yield Substitution(original, result)


class TestKnown(TestCase):
    def test_transcriptions(self) -> None:
        for transcription in load_transcriptions():
            self.assertEqual(
                list(map(str, IPA(transcription.transcription))),
                transcription.symbols,
            )

    def test_symbols(self) -> None:
        for symbol in load_symbols():
            ipa_symbol = IPASymbol(symbol.symbol)
            self.assertEqual(
                [feature.value for feature in sorted(features)]
                if (features := ipa_symbol.features()) is not None
                else None,
                symbol.features,
            )
            self.assertEqual(
                list(map(str, ipa_symbol.components))
                if ipa_symbol.components is not None
                else None,
                symbol.components,
            )

    def test_substitutions(self) -> None:
        for substitution in load_substitutions():
            self.assertEqual(str(IPA(substitution.original, IPAConfig(substitutions=True))), substitution.result)
