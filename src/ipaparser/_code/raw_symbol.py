from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .features import Feature

__all__ = [
    'RawSymbol',
]


@dataclass(frozen=True)
class RawSymbol:
    string: str
    features: set[Feature]
    components: Optional[list[RawSymbol]]
