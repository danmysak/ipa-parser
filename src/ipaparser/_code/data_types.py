from dataclasses import dataclass
from enum import Enum

from .definitions import TranscriptionType
from .features import Feature, FeatureSet

__all__ = [
    'Bracket',
    'Combining',
    'CombiningData',
    'Data',
    'DataError',
    'InnerBracketData',
    'Letter',
    'LetterData',
    'OuterBracketData',
    'Position',
    'SubstitutionData',
    'Symbol',
    'SymbolData',
    'Tie',
    'TieData',
    'Transformation',
]


class DataError(Exception):
    pass


class Position(str, Enum):
    PRECEDING = 'preceding'
    FOLLOWING = 'following'


@dataclass(frozen=True)
class Combining:
    character: str
    position: Position

    def apply(self, string: str) -> str:
        return self.character + string if self.position == Position.PRECEDING else string + self.character


@dataclass(frozen=True)
class Transformation:
    feature: Feature
    positive: bool

    def apply(self, features: FeatureSet) -> FeatureSet:
        return features | {self.feature} if self.positive else features - {self.feature}


Letter = str  # guaranteed to be non-empty
Symbol = str  # guaranteed to be non-empty
LetterData = dict[Letter, FeatureSet]
SymbolData = dict[Symbol, Feature]
CombiningData = dict[Combining, list[tuple[Feature, Transformation]]]
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
    ties: TieData
    main_tie: Tie
    outer_brackets: OuterBracketData
    inner_brackets: InnerBracketData
    substitutions: SubstitutionData
