from __future__ import annotations
from operator import attrgetter
from typing import Iterable, Optional, overload, Type, TypeVar, Union

from .features import Feature
from .ipa_config import IPAConfig
from .parser import parse
from .phonetics import unknown
from .symbol_data import SymbolData

__all__ = [
    'IPASymbol',
    'symbol_from_data',
]

F = TypeVar('F', bound=Feature)


class IPASymbol:
    _string: str
    _features: frozenset[Feature]

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
            self._set_data(SymbolData(
                string=data.normalized,
                features=unknown(),
            ), None)

    @overload
    def features(self) -> frozenset[Feature]:
        ...

    @overload
    def features(self, kind: Type[F]) -> frozenset[F]:
        ...

    @overload
    def features(self, kinds: set[Type[Feature]]) -> frozenset[Feature]:
        ...

    def features(self, kinds: Optional[Union[Type[Feature], Iterable[Type[Feature]]]] = None) -> frozenset[Feature]:
        if kinds is None:
            return self._features
        kind_list: list[Type[Feature]] = ([kinds]
                                          if isinstance(kinds, type) and issubclass(kinds, Feature)
                                          else list(kinds))  # noqa
        return frozenset(feature for feature in self._features
                         if any(isinstance(feature, kind) for kind in kind_list))

    def _set_data(self, data: SymbolData, components: Optional[list[SymbolData]]) -> None:
        self._string = data.string
        self._features = frozenset(data.features)
        self._components = (tuple(IPASymbol._from_data(component, None) for component in components)
                            if components is not None else None)

    @staticmethod
    def _from_data(data: SymbolData, components: Optional[list[SymbolData]]) -> IPASymbol:
        symbol = IPASymbol.__new__(IPASymbol)
        symbol._set_data(data, components)
        return symbol


symbol_from_data = (
    # So that package-level privacy of _from_data is maintained
    IPASymbol._from_data  # noqa
)
