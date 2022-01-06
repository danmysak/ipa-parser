from dataclasses import dataclass
from enum import Enum

from .definitions import TranscriptionType
from .features import Feature, FeatureSet

__all__ = [
    'Bracket',
    'Combining',
    'CombiningData',
    'CombiningType',
    'Data',
    'DataError',
    'InnerBracketData',
    'Letter',
    'LetterData',
    'OuterBracketData',
    'SubstitutionData',
    'Symbol',
    'SymbolData',
    'Tie',
    'TieData',
    'Transformation',
]


class DataError(Exception):
    pass


class CombiningType(str, Enum):
    DIACRITIC = 'diacritic'
    FOLLOWING = 'following'
    PRECEDING = 'preceding'


@dataclass(frozen=True)
class Combining:
    character: str
    type: CombiningType

    def apply(self, string: str) -> str:
        return self.character + string if self.type == CombiningType.PRECEDING else string + self.character


@dataclass(frozen=True)
class Transformation:
    required: Feature
    altered: Feature
    is_positive: bool

    def is_applicable(self, features: FeatureSet) -> bool:
        return self.required in features and (self.altered in features) != self.is_positive

    def apply(self, features: FeatureSet) -> FeatureSet:
        return features | {self.altered} if self.is_positive else features - {self.altered}


Letter = str  # guaranteed to be non-empty
Symbol = str  # guaranteed to be non-empty
LetterData = dict[Letter, FeatureSet]
SymbolData = dict[Symbol, Feature]
CombiningData = dict[Combining, list[Transformation]]
Tie = str  # guaranteed to be of length 1
TieData = set[Tie]
Bracket = str  # guaranteed to be of length 1
OuterBracketData = dict[tuple[Bracket, Bracket], TranscriptionType]
InnerBracketData = list[tuple[Bracket, Bracket]]
SubstitutionData = list[tuple[str, str]]


@dataclass(frozen=True)
class Data:
    consonants: LetterData
    vowels: LetterData
    breaks: SymbolData
    suprasegmentals: SymbolData
    combining_basic: CombiningData
    combining_recursive: CombiningData
    combining_meta: CombiningData
    ties: TieData
    main_tie: Tie
    outer_brackets: OuterBracketData
    inner_brackets: InnerBracketData
    substitutions: SubstitutionData
