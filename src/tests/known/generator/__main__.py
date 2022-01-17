from pathlib import Path
from typing import Iterable, Optional
from unicodedata import normalize

from ....ipaparser import IPA, IPAConfig, IPASymbol
from ....ipaparser.definitions import BracketStrategy
from ....ipaparser.features import Feature, FEATURE_KINDS, FeatureSet

DIRECTORY = Path(__file__).parent
PARENT_DIRECTORY = DIRECTORY.parent
INPUT_CORPUS = DIRECTORY / 'corpus'
OUTPUT_TRANSCRIPTIONS = PARENT_DIRECTORY / 'transcriptions'
OUTPUT_SYMBOLS = PARENT_DIRECTORY / 'symbols'
OUTPUT_SUBSTITUTIONS = PARENT_DIRECTORY / 'substitutions'

COLUMN_DELIMITER = '\t'
VALUE_DELIMITER = ', '
NO_DATA = '—'

transcriptions: set[str] = set()
symbols: set[str] = set()
substitutions: set[str] = set()


def format_line(*items: str) -> str:
    return COLUMN_DELIMITER.join(items)


def format_components(components: Optional[Iterable[IPASymbol]]) -> str:
    return VALUE_DELIMITER.join(str(component) for component in components) if components is not None else NO_DATA


def format_features(features: Optional[FeatureSet]) -> str:
    return VALUE_DELIMITER.join(feature.value for feature in sorted(features)) if features is not None else NO_DATA


def process_symbol(symbol: IPASymbol) -> None:
    interpretations = [symbol.features()]
    for kind in FEATURE_KINDS:
        for feature in kind:
            feature: Feature
            if (features := symbol.features(role=feature)) is not None and features not in interpretations:
                interpretations.append(features)
    symbols.add(format_line(
        str(symbol),
        format_components(symbol.components),
        *map(format_features, interpretations),
    ))
    for component in (symbol.components or []):
        process_symbol(component)


def process_transcription_and_symbols(transcription: str) -> None:
    for config in [IPAConfig(), IPAConfig(substitutions=True, brackets=BracketStrategy.EXPAND)]:
        ipa = IPA(transcription, config)
        transcriptions.add(format_line(str(ipa), VALUE_DELIMITER.join(str(symbol) for symbol in ipa)))
        for symbol in ipa:
            process_symbol(symbol)


def process_substitutions(transcription: str) -> None:
    assert normalize('NFD', transcription) == transcription
    assert str(IPA(transcription)) == transcription
    with_substitutions = str(IPA(transcription, IPAConfig(substitutions=True)))
    if with_substitutions != transcription:
        substitutions.add(format_line(transcription, with_substitutions))


with open(INPUT_CORPUS, 'r') as input_corpus:
    for unstripped in input_corpus:
        line = unstripped.rstrip('\n')
        process_transcription_and_symbols(line)
        process_substitutions(line)


for file, data in (
    (OUTPUT_TRANSCRIPTIONS, transcriptions),
    (OUTPUT_SYMBOLS, symbols),
    (OUTPUT_SUBSTITUTIONS, substitutions),
):
    with open(file, 'w') as output:
        output.write('\n'.join(sorted(data)) + '\n')
