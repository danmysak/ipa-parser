from collections import Counter, defaultdict
from math import floor
from pathlib import Path
from typing import Iterable

from ...ipaparser import IPA, IPASymbol
from ...ipaparser.features import Feature, FEATURE_KINDS, FeatureKind

KIND_HEADING = 'Kind'
FEATURE_HEADING = 'Feature'
STRING_HEADING = 'String representation'
EXAMPLES_HEADING = 'Examples'
SOURCES_HEADING = 'Sources'

CORPUS = Path(__file__).parent / 'corpus'
EXAMPLE_COUNT = 3
EXAMPLE_DELIMITER = ', '

SOURCE_BRACKETS = '[', ']'
SOURCE_DELIMITER = ', '
SOURCE_URL_REQUIRED_PREFIX = 'http'

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


FEATURE_INDEX = build_feature_index(extract_symbols())


def select(values: list[str], count: int) -> list[str]:
    threshold = floor((len(values) - 1) * SELECT_THRESHOLD)
    if count >= threshold:
        return values[:count]
    else:
        allowed = values[:threshold]
        taken: list[str] = [values[0]]
        while len(taken) < count:
            taken_characters = set(''.join(taken))
            _, best = min(
                enumerate(allowed), key=lambda value: (
                    len(set(value[1]).intersection(taken_characters)),  # maximizing uniqueness
                    1 if value[1] in taken else 0,  # avoiding duplicates
                    -value[0],  # maximizing information value
                ),
            )
            assert best not in taken
            taken.append(best)
        return taken


def parse_urls(docstring: str) -> list[str]:
    return [line
            for unstripped in docstring.strip().split('\n')
            if (line := unstripped.strip()).startswith(SOURCE_URL_REQUIRED_PREFIX)]


def wrap_code(code: str) -> str:
    return f'<code>{code}</code>'


def format_source(url: str, number: int) -> str:
    return f'<a href="{url}">{SOURCE_BRACKETS[0]}{number}{SOURCE_BRACKETS[1]}</a>'


def merge_lines(lines: Iterable[str]) -> str:
    return '\n'.join(lines)


def build_feature_cells(feature: Feature, kind: FeatureKind) -> str:
    examples = EXAMPLE_DELIMITER.join(map(wrap_code, select(list(map(str, FEATURE_INDEX[feature])), EXAMPLE_COUNT)))
    return f"""
    <td>{wrap_code(kind.__name__ + '.' + feature.name)}</td>
    <td>{wrap_code(feature.value)}</td>
    <td>{examples}</td>
    """


def build_kind_rows(kind: FeatureKind) -> str:
    string_representations = [value for value in kind.kind_values() if value != kind.__name__]
    assert len(string_representations) == 1
    string, = string_representations
    sources = SOURCE_DELIMITER.join(format_source(url, index + 1)
                                    for index, url in enumerate(parse_urls(kind.__doc__)))
    features = list(kind)
    first_feature, rest_of_features = features[0], features[1:]
    return merge_lines([f"""
    <tr>
    <td align="center" rowspan="{len(kind)}">{wrap_code(kind.__name__)}<br>{wrap_code(f"'{string}'")}</td>
    {build_feature_cells(first_feature, kind)}
    <td align="center" rowspan="{len(kind)}">{sources}</td>
    </tr>
    """] + [f"""
    <tr>
    {build_feature_cells(feature, kind)}
    </tr>
    """ for feature in rest_of_features])


def build_table() -> str:
    return f"""
    <table>
    <thead>
    <tr>
    <th>{KIND_HEADING}</th>
    <th>{FEATURE_HEADING}</th>
    <th>{STRING_HEADING}</th>
    <th>{EXAMPLES_HEADING}</th>
    <th>{SOURCES_HEADING}</th>
    </tr>
    </thead>
    <tbody>
    {merge_lines(build_kind_rows(kind) for kind in FEATURE_KINDS)}
    </tbody>
    </table>
    """


def clean_up_table(table: str) -> str:
    return '\n'.join([stripped for line in table.split('\n') if (stripped := line.strip())])


print(clean_up_table(build_table()))
