from __future__ import annotations
from operator import attrgetter
from typing import Optional

from .features import Feature
from .ipa_config import IPAConfig
from .ipa_data import IPAData
from .parser import parse
from .phonetics import unknown

__all__ = [
    'IPASymbol',
]


class IPASymbol:
    _string: str

    _features: frozenset[Feature]
    features: frozenset[Feature] = property(attrgetter('_features'))

    _components: Optional[tuple[IPASymbol, ...]]
    components: Optional[tuple[IPASymbol, ...]] = property(attrgetter('_components'))

    @property
    def left(self) -> Optional[IPASymbol]:
        """Get the first component of the symbol, if there are any (None otherwise)."""
        return self._components[0] if self._components else None

    @property
    def middle(self) -> Optional[IPASymbol]:
        """Get the middle component of the symbol, if the number of components is odd (None otherwise)."""
        length = len(self._components or [])
        return self._components[(length - 1) // 2] if length % 2 == 1 else None

    @property
    def right(self) -> Optional[IPASymbol]:
        """Get the last component of the symbol, if there are any (None otherwise)."""
        return self._components[-1] if self._components else None

    def __str__(self) -> str:
        return self._string

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({repr(str(self))})'

    def __init__(self, string: str, config: IPAConfig = IPAConfig()) -> None:
        """Parse a single sound or auxiliary IPA symbol.

        :param string: The string to parse (like 'a', 'pʰ', '˦', or 'ˈˈ').
        :param config: Parsing parameters.
        """
        data = parse(string, config)
        symbol = next(data.symbols, None)
        if symbol and symbol.is_last:
            self._set_data(symbol.data, symbol.components)
        else:
            self._set_data(IPAData(
                string=data.normalized,
                features=unknown(),
            ), None)

    @staticmethod
    def from_data(data: IPAData, components: Optional[list[IPAData]] = None) -> IPASymbol:
        """Initialize a symbol directly with the provided data.

        :param data: Spelling and features of the symbol.
        :param components: Spellings and features of the components, or None if there are none.
        :return: The symbol.
        """
        symbol = IPASymbol.__new__(IPASymbol)
        symbol._set_data(data, components)
        return symbol

    def _set_data(self, data: IPAData, components: Optional[list[IPAData]]) -> None:
        self._string = data.string
        self._features = frozenset(data.features)
        self._components = (tuple(IPASymbol.from_data(component) for component in components)
                            if components is not None else None)
