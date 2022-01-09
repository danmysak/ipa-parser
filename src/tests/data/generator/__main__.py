from pathlib import Path
from typing import Iterable, Optional

from ....ipaparser import IPA, IPAConfig, IPASymbol
from ....ipaparser.definitions import BracketStrategy
from ....ipaparser.features import FeatureSet

DIRECTORY = Path(__file__).parent
INPUT_CORPUS = DIRECTORY / 'corpus'
OUTPUT_TRANSCRIPTIONS = DIRECTORY.parent / 'transcriptions'
OUTPUT_SYMBOLS = DIRECTORY.parent / 'symbols'

COLUMN_DELIMITER = '\t'
VALUE_DELIMITER = ', '
NO_DATA = '—'

transcriptions: set[str] = set()
symbols: set[str] = set()


def format_line(*items: str) -> str:
    return COLUMN_DELIMITER.join(items)


def format_components(components: Optional[Iterable[IPASymbol]]) -> str:
    return VALUE_DELIMITER.join(str(component) for component in components) if components is not None else NO_DATA


def format_features(features: Optional[FeatureSet]) -> str:
    return VALUE_DELIMITER.join(feature.value for feature in sorted(features)) if features is not None else NO_DATA


def process_symbol(symbol: IPASymbol) -> None:
    symbols.add(format_line(
        str(symbol),
        format_components(symbol.components),
        format_features(symbol.features()),
    ))
    for component in symbol.components or []:
        process_symbol(component)


with open(INPUT_CORPUS, 'r') as input_corpus:
    for unstripped in input_corpus:
        transcription = unstripped.rstrip('\n')
        ipa = IPA(transcription, IPAConfig(
            substitutions=True,
            brackets=BracketStrategy.EXPAND,
        ))
        transcriptions.add(format_line(str(ipa), VALUE_DELIMITER.join(str(symbol) for symbol in ipa)))
        for symbol in ipa:
            process_symbol(symbol)

for file, data in ((OUTPUT_SYMBOLS, symbols),
                   (OUTPUT_TRANSCRIPTIONS, transcriptions)):
    with open(file, 'w') as output:
        output.write('\n'.join(sorted(data)) + '\n')
