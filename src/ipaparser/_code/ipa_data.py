from dataclasses import dataclass

from .features import Feature

__all__ = [
    'IPAData',
]


@dataclass(frozen=True)
class IPAData:
    string: str
    features: set[Feature]
