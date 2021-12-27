from dataclasses import dataclass
from typing import Iterable

from .features import Feature

__all__ = [
    'SymbolData',
]


@dataclass(frozen=True)
class SymbolData:
    string: str
    features: Iterable[Feature]
