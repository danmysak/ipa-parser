from collections import Counter, defaultdict
from math import floor
from pathlib import Path
from typing import Iterable

from ...ipaparser import IPA, IPASymbol
from ...ipaparser.features import Feature, FEATURE_KINDS, FeatureKind

KIND_HEADING = 'Kind'
FEATURE_HEADING = 'Feature'
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


def select(values: list[IPASymbol], count: int, feature_of_interest: Feature) -> list[IPASymbol]:
    threshold = floor((len(values) - 1) * SELECT_THRESHOLD)
    if count >= threshold:
        return values[:count]
    else:
        allowed = values[:threshold]
        taken: list[IPASymbol] = []
        taken_characters: set[str] = set()
        taken_features: set[Feature] = set()

        def add(symbol: IPASymbol) -> None:
            taken.append(symbol)
            taken_characters.update(character for character in str(symbol))
            taken_features.update(feature for feature in (symbol.features() or {}))

        def sorting_key(enumerated: tuple[int, IPASymbol]) -> tuple[int, ...]:
            index, symbol = enumerated
            return (
                len([feature for feature in (symbol.features() or {})
                     if feature in taken_features and feature.derived() == feature_of_interest]),
                # disambiguating features such as height and backness categories

                len(set(str(symbol)).intersection(taken_characters)),  # maximizing uniqueness
                1 if symbol in taken else 0,  # avoiding duplicates
                -index,  # maximizing information value
            )

        add(values[0])
        while len(taken) < count:
            _, best = min(enumerate(allowed), key=sorting_key)
            assert best not in taken
            add(best)
        return taken


def parse_urls(docstring: str) -> list[str]:
    return [line
            for unstripped in docstring.strip().split('\n')
            if (line := unstripped.strip()).startswith(SOURCE_URL_REQUIRED_PREFIX)]


def wrap_code(code: str) -> str:
    return f'<code>{code}</code>'


def wrap_string(string: str) -> str:
    return wrap_code(f"'{string}'")


def format_source(url: str, number: int) -> str:
    return f'<a href="{url}">{SOURCE_BRACKETS[0]}{number}{SOURCE_BRACKETS[1]}</a>'


def merge_lines(lines: Iterable[str]) -> str:
    return '\n'.join(lines)


def build_feature_cells(feature: Feature) -> str:
    return f"""
    <td>{wrap_code(feature.name)}<br>{wrap_string(feature.value)}</td>
    <td>{EXAMPLE_DELIMITER.join(map(wrap_code, map(str, select(FEATURE_INDEX[feature], EXAMPLE_COUNT, feature))))}</td>
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
    <td align="center" rowspan="{len(kind)}">{wrap_code(kind.__name__)}<br>{wrap_string(string)}</td>
    {build_feature_cells(first_feature)}
    <td align="center" rowspan="{len(kind)}">{sources}</td>
    </tr>
    """] + [f"""
    <tr>
    {build_feature_cells(feature)}
    </tr>
    """ for feature in rest_of_features])


def build_table() -> str:
    return f"""
    <table>
    <thead>
    <tr>
    <th>{KIND_HEADING}</th>
    <th>{FEATURE_HEADING}</th>
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
