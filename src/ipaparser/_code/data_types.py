from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .definitions import TranscriptionType
from .features import Feature, FeatureSet

__all__ = [
    'Bracket',
    'Change',
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
class Change:
    feature: Feature
    is_positive: bool


@dataclass(frozen=True)
class Transformation:
    required: Optional[Feature] = None
    incompatible: Optional[FeatureSet] = None
    change: Optional[Change] = None

    def is_applicable(self, features: FeatureSet) -> bool:
        return ((self.required is None or self.required in features)
                and (self.incompatible is None or features.isdisjoint(self.incompatible))
                and (self.change is None or (self.change.feature in features) != self.change.is_positive))

    def apply(self, features: FeatureSet) -> FeatureSet:
        if self.change is None:
            return features
        elif self.change.is_positive:
            return features | {self.change.feature}
        else:
            return features - {self.change.feature}


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
