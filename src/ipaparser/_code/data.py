from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional
import unicodedata

from .features import Feature, parse_feature
from .definitions.transcription import TranscriptionType

__all__ = [
    'BracketData',
    'Combining',
    'CombiningData',
    'Data',
    'get_data',
    'LetterData',
    'load_data',
    'Position',
    'SubstitutionData',
    'SymbolData',
    'TieData',
    'Transformation',
]

COLUMN_DELIMITER = '\t'
VALUE_DELIMITER = ', '
PLACEHOLDER = '◌'
NEGATIVE_PREFIX = '-'

DIRECTORY = Path(__file__).parent.parent / '_data'

LETTERS = 'letters'
CONSONANTS = f'{LETTERS}/consonants.tsv'
VOWELS = f'{LETTERS}/vowels.tsv'
BREAKS = 'breaks'
SUPRASEGMENTALS = 'suprasegmentals'
COMBINING_BASIC = 'combining-basic'
COMBINING_RECURSIVE = 'combining-recursive'
TIES = 'ties'
BRACKETS = 'brackets'
SUBSTITUTIONS = 'substitutions'


class Position(str, Enum):
    PRECEDING = 'preceding'
    FOLLOWING = 'following'


@dataclass(frozen=True)
class Combining:
    character: str
    position: Position


@dataclass(frozen=True)
class Transformation:
    feature: Feature
    positive: bool


TabularData = list[list[list[str]]]  # rows, columns, cell values

LetterData = dict[str, set[Feature]]
SymbolData = dict[str, Feature]
CombiningData = dict[Combining, list[tuple[Feature, Transformation]]]
TieData = set[str]
BracketData = dict[tuple[str, str], Optional[TranscriptionType]]
SubstitutionData = list[tuple[str, str]]


@dataclass
class Data:
    consonants: LetterData
    vowels: LetterData
    breaks: SymbolData
    suprasegmentals: SymbolData
    combining_basic: CombiningData
    combining_recursive: CombiningData
    ties: TieData
    brackets: BracketData
    substitutions: SubstitutionData


DATA: Optional[Data] = None


def read(filename: str) -> TabularData:
    file = DIRECTORY / filename
    if not file.exists():
        raise ValueError(f'Data file does not exist: {file}')
    with open(file, 'r') as data:
        return [[column.split(VALUE_DELIMITER) if column else []
                 for column in line.split(COLUMN_DELIMITER)]
                for unstripped in data
                if (line := unstripped.rstrip('\n'))]


def parse_letter_data(data: TabularData) -> LetterData:
    row_count = len(data)
    if row_count == 0:
        raise ValueError(f'Letter data must contain some rows')
    column_count = len(data[0])
    if column_count == 0:
        raise ValueError(f'Letter data must contain some columns')
    if any(len(row) != column_count for row in data):
        raise ValueError(f'Letter data must be a rectangular grid')

    def to_features(values: list[str]) -> set[Feature]:
        return set(map(parse_feature, values))

    column_sets = [to_features(column) for column in data[0]]
    row_sets = [to_features(row[0]) for row in data]
    mapping: LetterData = {}
    for row_index in range(1, row_count):
        for column_index in range(1, column_count):
            for letter in data[row_index][column_index]:
                if letter in mapping:
                    raise ValueError(f'The letter "{letter}" is encountered in data multiple times')
                mapping[letter] = row_sets[row_index] | column_sets[column_index]
    return mapping


def parse_symbol_data(data: TabularData) -> SymbolData:
    mapping: SymbolData = {}
    for row in data:
        if len(row) != 2:
            raise ValueError(f'Each row must contain exactly two columns')
        symbols, features = row
        if len(features) != 1:
            raise ValueError(f'Expected exactly one feature, got "{VALUE_DELIMITER.join(features)}"')
        feature = features[0]
        for symbol in symbols:
            if symbol in mapping:
                raise ValueError(f'The symbol "{symbol}" is encountered in data multiple times')
            mapping[symbol] = feature
    return mapping


def parse_combining(definition: str) -> Combining:
    if len(definition) != 2 or (definition.startswith(PLACEHOLDER) == definition.endswith(PLACEHOLDER)):
        raise ValueError(f'Invalid combining format: "{definition}"')
    if definition.startswith(PLACEHOLDER):
        return Combining(definition.removeprefix(PLACEHOLDER), Position.FOLLOWING)
    else:
        prefix = definition.removesuffix(PLACEHOLDER)
        if unicodedata.combining(prefix):
            raise ValueError(f'Definition starts with a combining character: "{" " + definition}"')
        return Combining(prefix, Position.PRECEDING)


def parse_transformation(definition: str) -> Transformation:
    return Transformation(
        parse_feature(definition.removeprefix(NEGATIVE_PREFIX)),
        not definition.startswith(NEGATIVE_PREFIX),
    )


def parse_combining_data(data: TabularData) -> CombiningData:
    mapping: CombiningData = {}
    for row in data:
        if len(row) != 3:
            raise ValueError(f'Expected exactly three columns in each row')
        characters, requirements, transformations = row
        if len(requirements) != 1:
            raise ValueError(f'Expected exactly one required feature, got "{VALUE_DELIMITER.join(requirements)}"')
        required_feature = parse_feature(requirements[0])
        to_append = [(required_feature, parse_transformation(transformation)) for transformation in transformations]
        for definition in characters:
            combining = parse_combining(definition)
            if combining not in mapping:
                mapping[combining] = []
            mapping[combining].extend(to_append)
    return mapping


def parse_tie_data(data: TabularData) -> TieData:
    ties: TieData = set()
    for row in data:
        if len(row) != 1:
            raise ValueError(f'Expected exactly one column in each row')
        if len(row[0]) != 1:
            raise ValueError(f'Expected exactly one value in each cell')
        value = row[0][0]
        if len(value) != 3 or not value.startswith(PLACEHOLDER) or not value.endswith(PLACEHOLDER):
            raise ValueError(f'Expected value in the format "{PLACEHOLDER}(tie){PLACEHOLDER}", got "{value}"')
        tie = value.removeprefix(PLACEHOLDER).removesuffix(PLACEHOLDER)
        if tie in ties:
            raise ValueError(f'The tie "{value}" is encountered in data multiple times')
        ties.add(tie)
    return ties


def parse_bracket_data(data: TabularData) -> BracketData:
    mapping: BracketData = {}
    for row in data:
        if len(row) < 2:
            raise ValueError(f'Expected at least two columns with opening and closing brackets in each row')
        if any(len(column) != 1 for column in row):
            raise ValueError(f'Expected exactly one value in each cell')
        opening, closing, rest = row[0][0], row[1][0], row[2:]
        if len(rest) > 1:
            raise ValueError(f'Unexpected trailing values')
        key = opening, closing
        if key in mapping:
            raise ValueError(f'The bracket pair "{opening}"/"{closing}" is encountered in data multiple times')
        mapping[key] = TranscriptionType(rest[0]) if rest else None
    return mapping


def parse_substitution_data(data: TabularData) -> SubstitutionData:
    substitutions: SubstitutionData = []
    for row in data:
        if len(row) != 2:
            raise ValueError(f'Expected exactly two columns in each row')
        if any(len(column) != 1 for column in row):
            raise ValueError(f'Expected exactly one value in each cell')
        substitutions.append((row[0][0], row[1][0]))
    return substitutions


def get_data() -> Data:
    global DATA
    if DATA is None:
        DATA = Data(
            consonants=parse_letter_data(read(CONSONANTS)),
            vowels=parse_letter_data(read(VOWELS)),
            breaks=parse_symbol_data(read(BREAKS)),
            suprasegmentals=parse_symbol_data(read(SUPRASEGMENTALS)),
            combining_basic=parse_combining_data(read(COMBINING_BASIC)),
            combining_recursive=parse_combining_data(read(COMBINING_RECURSIVE)),
            ties=parse_tie_data(read(TIES)),
            brackets=parse_bracket_data(read(BRACKETS)),
            substitutions=parse_substitution_data(read(SUBSTITUTIONS)),
        )
    return DATA


def load_data() -> None:
    """Preemptively load supporting data from disk so that the first parse is a bit faster."""
    get_data()
