from collections import Counter, defaultdict
import math
from pathlib import Path
from string import Template
from typing import Iterable

from ...ipaparser import IPA, IPASymbol
from ...ipaparser.features import Feature, FEATURE_KINDS

CORPUS = Path(__file__).parent / 'corpus'

HEADING_TEMPLATE = "#### `$kind`/`'$string'` $sources"
SOURCE_TEMPLATE = '[$number]'
SOURCE_DELIMITER = ', '
URL_REQUIRED_PREFIX = 'http'

VALUE_HEADING = 'Value'
STRING_HEADING = 'String representation'
EXAMPLES_HEADING = 'Examples'
EXAMPLE_COUNT = 3
EXAMPLE_DELIMITER = ', '

SELECT_THRESHOLD = 0.5


def extract_symbols() -> Counter[IPASymbol]:
    counter: Counter[IPASymbol] = Counter()
    with open(CORPUS, 'r') as corpus:
        for unstripped in corpus:
            for symbol in IPA(unstripped.strip()):
                counter[symbol] += 1
    return counter


def build_feature_index(symbols: Counter[IPASymbol]) -> defaultdict[Feature, list[IPASymbol]]:
    feature_index: defaultdict[Feature, list[IPASymbol]] = defaultdict(list)
    for symbol, _ in symbols.most_common():
        for feature in (symbol.features() or {}):
            if symbol not in feature_index[feature]:
                feature_index[feature].append(symbol)
    return feature_index


def select(values: list[str], count: int) -> list[str]:
    threshold = math.floor((len(values) - 1) * SELECT_THRESHOLD)
    if count >= threshold:
        return values[:count]
    else:
        allowed = values[:threshold]
        taken: list[str] = [values[0]]
        while len(taken) < count:
            taken_characters = set(''.join(taken))
            _, best = min(
                enumerate(allowed),
                key=lambda value: (len(set(value[1]).intersection(taken_characters)), -value[0]),
                # First component gives more uniqueness, second is so that values are more exotic
            )
            if best in taken:
                break
            taken.append(best)
        return taken


def parse_urls(docstring: str) -> list[str]:
    return [line
            for unstripped in docstring.strip().split('\n')
            if (line := unstripped.strip()).startswith(URL_REQUIRED_PREFIX)]


def format_source(url: str, number: int) -> str:
    text = Template(SOURCE_TEMPLATE).substitute({
        "number": number,
    })
    return f'[{text}]({url})'


def format_symbol(symbol: str) -> str:
    return f'`{symbol}`'


def format_table(values: list[list[str]]) -> str:
    column_count = len(values[0])
    column_lengths = [max(*(len(row[i]) for row in values)) for i in range(column_count)]
    lines: list[str] = []

    def add_line(line: Iterable[str]) -> None:
        lines.append(f'| {" | ".join(line)} |')

    for row_index, row in enumerate(values):
        add_line(row[i].ljust(column_lengths[i]) for i in range(column_count))
        if row_index == 0:
            add_line('-' * column_lengths[i] for i in range(column_count))

    return '\n'.join(lines)


def run() -> None:
    feature_index = build_feature_index(extract_symbols())

    for kind in FEATURE_KINDS:
        string_representations = [value for value in kind.kind_values() if value != kind.__name__]
        assert len(string_representations) == 1
        print(Template(HEADING_TEMPLATE).substitute({
            'kind': kind.__name__,
            'string': string_representations[0],
            'sources': SOURCE_DELIMITER.join(format_source(url, index + 1)
                                             for index, url in enumerate(parse_urls(kind.__doc__))),
        }).strip())

        table: list[list[str]] = [[VALUE_HEADING, STRING_HEADING, EXAMPLES_HEADING]]
        feature: Feature
        for feature in kind:
            table.append([
                f'`{kind.__name__}.{feature.name}`',
                f'`{feature.value}`',
                EXAMPLE_DELIMITER.join(
                    map(format_symbol, select(list(map(str, feature_index[feature])), EXAMPLE_COUNT))
                ),
            ])
        print(format_table(table))
        print('')


run()
