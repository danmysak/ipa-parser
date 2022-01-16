from pathlib import Path
from typing import Optional
import unicodedata

from .cacher import with_cache
from .data_types import (
    Bracket,
    Change,
    Combining,
    CombiningData,
    CombiningType,
    Data,
    DataError,
    InnerBracketData,
    OuterBracketData,
    SubstitutionData,
    Symbol,
    Tie,
    TieData,
    Transformation,
)
from .definitions import TranscriptionType
from .feature_helper import find_feature, find_feature_kind
from .features import Feature, FeatureKind, FeatureSet
from .strings import is_decomposed

__all__ = [
    'get_data',
]

COLUMN_DELIMITER = '\t'
VALUE_DELIMITER = ', '
DISJUNCTION_DELIMITER = ' | '
CONJUNCTION_DELIMITER = ' & '
PLACEHOLDER = '◌'
ADD_PREFIX = '+'
SUBTRACT_PREFIX = '-'
NO_CHANGE = '='
INCOMPATIBLE_PREFIX = '!'
META_BRACKETS = '(', ')'


DIRECTORY = Path(__file__).parent.parent / '_data'

LETTERS = 'letters'
CONSONANTS = f'{LETTERS}/consonants.tsv'
VOWELS = f'{LETTERS}/vowels.tsv'
BREAKS = 'breaks'
SUPRASEGMENTALS = 'suprasegmentals'
COMBINING_BASIC = 'combining-basic'
COMBINING_MAIN = 'combining-main'
COMBINING_META = 'combining-meta'
TIES = 'ties'
BRACKETS = 'brackets'
SUBSTITUTIONS = 'substitutions'


TabularData = list[list[list[str]]]  # rows, columns, cell values


def read(filename: str) -> TabularData:
    file = DIRECTORY / filename
    if not file.exists():
        raise DataError(f'Data file does not exist: {file}')
    data: TabularData = []
    with open(file, 'r') as contents:
        for unstripped in contents:
            line = unstripped.rstrip('\n')
            if not line:
                continue
            if not is_decomposed(line):
                raise DataError(f'Line is not normalized: "{line}"')
            data.append([column.split(VALUE_DELIMITER) if column else []
                         for column in line.split(COLUMN_DELIMITER)])
    return data


def get_feature(value: str) -> Feature:
    feature = find_feature(value)
    if feature is None:
        raise DataError(f'Unknown feature: "{value}"')
    return feature


def get_feature_conjunction(value: str) -> FeatureSet:
    return frozenset(map(get_feature, value.split(CONJUNCTION_DELIMITER)))


def get_feature_kind(value: str) -> FeatureKind:
    kind = find_feature_kind(value)
    if kind is None:
        raise DataError(f'Unknown feature kind: "{value}"')
    return kind


def parse_symbol(string: str, features: FeatureSet) -> Symbol:
    left_bracket, right_bracket = META_BRACKETS
    is_alternative = string.startswith(left_bracket) and string.endswith(right_bracket)
    symbol = string.removeprefix(left_bracket).removesuffix(right_bracket) if is_alternative else string
    if not symbol:
        raise DataError(f'No empty symbols allowed')
    return Symbol(
        string=symbol,
        is_main_interpretation=not is_alternative,
        features=features,
    )


def parse_letter_data(data: TabularData) -> set[Symbol]:
    row_count = len(data)
    if row_count == 0:
        raise DataError(f'Letter data must contain some rows')
    column_count = len(data[0])
    if column_count == 0:
        raise DataError(f'Letter data must contain some columns')
    if any(len(row) != column_count for row in data):
        raise DataError(f'Letter data must be a rectangular grid')

    def to_features(values: list[str]) -> FeatureSet:
        return frozenset(map(get_feature, values))

    common_set = to_features(data[0][0])
    column_sets = [to_features(column) for column in data[0]]
    row_sets = [to_features(row[0]) for row in data]
    letters: set[Symbol] = set()
    for row_index in range(1, row_count):
        for column_index in range(1, column_count):
            for letter in data[row_index][column_index]:
                letters.add(parse_symbol(letter, common_set | row_sets[row_index] | column_sets[column_index]))
    return letters


def parse_non_letter_symbol_data(data: TabularData) -> set[Symbol]:
    symbols: set[Symbol] = set()
    for row in data:
        if len(row) != 2:
            raise DataError(f'Each row must contain exactly two columns')
        symbol_options, features = row
        if not symbol_options:
            raise DataError(f'Expected at least one symbol')
        if len(features) != 1:
            raise DataError(f'Expected exactly one feature, got "{VALUE_DELIMITER.join(features)}"')
        for symbol in symbol_options:
            symbols.add(parse_symbol(symbol, frozenset({get_feature(features[0])})))
    return symbols


def parse_combining(definition: str) -> Combining:
    if (len(definition) != 1 + len(PLACEHOLDER)
            or definition.startswith(PLACEHOLDER) == definition.endswith(PLACEHOLDER)):
        raise DataError(f'Invalid combining format or a combining string is longer than one character: "{definition}"')
    if definition.startswith(PLACEHOLDER):
        character = definition.removeprefix(PLACEHOLDER)
        return Combining(
            character=character,
            type=CombiningType.DIACRITIC if unicodedata.combining(character) else CombiningType.FOLLOWING,
        )
    else:
        character = definition.removesuffix(PLACEHOLDER)
        if unicodedata.combining(character):
            raise DataError(f'Definition starts with a combining character: "{" " + definition}"')
        return Combining(
            character=character,
            type=CombiningType.PRECEDING,
        )


def parse_incompatible(definition: str) -> FeatureSet:
    if not definition.startswith(INCOMPATIBLE_PREFIX):
        raise DataError(f'Definition of incompatible features must start with "{INCOMPATIBLE_PREFIX}",'
                        f' got "{definition}"')
    value = definition.removeprefix(INCOMPATIBLE_PREFIX)
    left_bracket, right_bracket = META_BRACKETS
    return (frozenset(get_feature_kind(value.removeprefix(left_bracket).removesuffix(right_bracket)))
            if value.startswith(left_bracket) and value.endswith(right_bracket)
            else frozenset({get_feature(value)}))


def parse_change(definition: str) -> Optional[Change]:
    if definition == NO_CHANGE:
        return None
    for prefix, is_positive in ((ADD_PREFIX, True), (SUBTRACT_PREFIX, False)):
        if definition.startswith(prefix):
            return Change(
                feature=get_feature(definition.removeprefix(prefix)),
                is_positive=is_positive,
            )
    raise DataError(f'Expected either "{ADD_PREFIX}" or "{SUBTRACT_PREFIX}" in front of an altered feature'
                    f' (or "{NO_CHANGE}" for no altered features), got "{definition}"')


def parse_combining_data(data: TabularData) -> CombiningData:
    mapping: CombiningData = {}
    for row in data:
        if len(row) < 3:
            raise DataError(f'Expected at least three columns in each row, got {len(row)} in "{row}"')
        characters, requirements, changes, *incompatible_cells = row
        if len(incompatible_cells) > 1:
            raise DataError(f'Row has an unexpected tail: "{incompatible_cells[1:]}"')
        incompatible_content = incompatible_cells[0] if incompatible_cells else None
        if len(requirements) != 1:
            raise DataError(f'Expected exactly one required feature or boolean feature formula,'
                            f' got "{VALUE_DELIMITER.join(requirements)}"')
        required_feature_sets = map(get_feature_conjunction, requirements[0].split(DISJUNCTION_DELIMITER))
        if incompatible_content is not None:
            if not incompatible_content:
                raise DataError(f'Expected an incompatible feature or feature kind, got an empty cell')
            incompatible = frozenset().union(*map(parse_incompatible, incompatible_content))
        else:
            incompatible = frozenset()
        to_append = [Transformation(required, incompatible, tuple(filter(None, map(parse_change, changes))))
                     for required in required_feature_sets]
        for definition in characters:
            combining = parse_combining(definition)
            if combining not in mapping:
                mapping[combining] = []
            mapping[combining].extend(to_append)
    return mapping


def parse_tie_data(data: TabularData) -> tuple[TieData, Tie]:
    ties: list[Tie] = []
    for row in data:
        if len(row) != 1:
            raise DataError(f'Expected exactly one column in each row')
        if len(row[0]) != 1:
            raise DataError(f'Expected exactly one value in each cell')
        value = row[0][0]
        if (len(value) != 1 + 2 * len(PLACEHOLDER)
                or not value.startswith(PLACEHOLDER)
                or not value.endswith(PLACEHOLDER)):
            raise DataError(f'Expected value in the format "{PLACEHOLDER}(single-character tie){PLACEHOLDER}",'
                            f' got "{value}"')
        tie = value.removeprefix(PLACEHOLDER).removesuffix(PLACEHOLDER)
        if not unicodedata.combining(tie):
            raise DataError(f'The tie "{tie}" is not a combining character')
        if tie in ties:
            raise DataError(f'The tie "{value}" is encountered in data multiple times')
        ties.append(tie)
    if not ties:
        raise DataError(f'Expected to read at least one tie')
    return set(ties), ties[0]


def parse_bracket_data(data: TabularData) -> tuple[OuterBracketData, InnerBracketData]:
    outer: OuterBracketData = {}
    inner: InnerBracketData = []
    inner_index: set[Bracket] = set()
    for row in data:
        if len(row) < 2:
            raise DataError(f'Expected at least two columns with opening and closing brackets in each row')
        if any(len(column) != 1 for column in row):
            raise DataError(f'Expected exactly one value in each cell, got row {row}')
        opening, closing, rest = row[0][0], row[1][0], row[2:]
        if len(rest) > 1:
            raise DataError(f'Unexpected trailing values: {rest[1:]}')
        pair = opening, closing
        if any(len(bracket) != 1 for bracket in pair):
            raise DataError(f'Brackets are expected to be of length 1 (got "{opening}" and "{closing}")')
        if pair in outer or pair in inner:
            raise DataError(f'The bracket pair "{opening}" and "{closing}" is encountered in data multiple times')
        if rest:
            outer[pair] = TranscriptionType(rest[0][0])
        else:
            if not inner_index.isdisjoint(pair) or len(set(pair)) != 2:
                raise DataError(f'Inner brackets do not form unique opening-closing pairs')
            inner_index.update(pair)
            inner.append(pair)
    return outer, inner


def parse_substitution_data(data: TabularData) -> SubstitutionData:
    substitutions: SubstitutionData = []
    for row in data:
        if len(row) != 2:
            raise DataError(f'Expected exactly two columns in each row, got {row}')
        if any(len(column) != 1 for column in row):
            raise DataError(f'Expected exactly one value in each cell, got row {row}')
        substitutions.append((row[0][0], row[1][0]))
    return substitutions


def load_data() -> Data:
    ties, main_tie = parse_tie_data(read(TIES))
    outer_brackets, inner_brackets = parse_bracket_data(read(BRACKETS))
    return Data(
        consonants=parse_letter_data(read(CONSONANTS)),
        vowels=parse_letter_data(read(VOWELS)),
        breaks=parse_non_letter_symbol_data(read(BREAKS)),
        suprasegmentals=parse_non_letter_symbol_data(read(SUPRASEGMENTALS)),
        combining_basic=parse_combining_data(read(COMBINING_BASIC)),
        combining_main=parse_combining_data(read(COMBINING_MAIN)),
        combining_meta=parse_combining_data(read(COMBINING_META)),
        ties=ties,
        main_tie=main_tie,
        outer_brackets=outer_brackets,
        inner_brackets=inner_brackets,
        substitutions=parse_substitution_data(read(SUBSTITUTIONS)),
    )


get_data = with_cache(load_data)
