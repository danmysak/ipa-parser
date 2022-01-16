from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from .definitions import TranscriptionType
from .features import Feature, FeatureSet

__all__ = [
    'Bracket',
    'Change',
    'ChangeSequence',
    'Combining',
    'CombiningData',
    'CombiningType',
    'Data',
    'DataError',
    'InnerBracketData',
    'OuterBracketData',
    'SubstitutionData',
    'Symbol',
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

    def negate(self) -> Change:
        return Change(self.feature, not self.is_positive)


ChangeSequence = tuple[Change, ...]


@dataclass(frozen=True)
class Transformation:
    required: FeatureSet
    incompatible: FeatureSet
    changes: ChangeSequence

    def is_applicable(self, features: FeatureSet) -> bool:
        return (self.required <= features
                and features.isdisjoint(self.incompatible)
                and all((change.feature in features) != change.is_positive for change in self.changes))

    def apply(self, features: FeatureSet) -> FeatureSet:
        for change in self.changes:
            features = features | {change.feature} if change.is_positive else features - {change.feature}
        return features


@dataclass(frozen=True)
class Symbol:
    string: str  # guaranteed to be non-empty
    is_main_interpretation: bool
    features: FeatureSet


CombiningData = dict[Combining, list[Transformation]]
Tie = str  # guaranteed to be of length 1
TieData = set[Tie]
Bracket = str  # guaranteed to be of length 1
OuterBracketData = dict[tuple[Bracket, Bracket], TranscriptionType]
InnerBracketData = list[tuple[Bracket, Bracket]]
SubstitutionData = list[tuple[str, str]]


@dataclass(frozen=True)
class Data:
    consonants: set[Symbol]
    vowels: set[Symbol]
    breaks: set[Symbol]
    suprasegmentals: set[Symbol]
    combining_basic: CombiningData
    combining_main: CombiningData
    combining_meta: CombiningData
    ties: TieData
    main_tie: Tie
    outer_brackets: OuterBracketData
    inner_brackets: InnerBracketData
    substitutions: SubstitutionData
