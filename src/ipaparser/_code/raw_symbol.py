from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .features import FeatureSet

__all__ = [
    'RawSymbol',
]


@dataclass(frozen=True)
class RawSymbol:
    string: str
    features: Optional[FeatureSet] = None
    components: Optional[list[RawSymbol]] = None
