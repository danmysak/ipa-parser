from __future__ import annotations
from typing import Optional, overload, Type, TypeVar, Union

from .exceptions import FeatureKindError
from .feature_finder import find_feature_kind
from .features import Feature, FeatureSet
from .ipa_config import IPAConfig
from .parser import parse
from .raw_symbol import RawSymbol

__all__ = [
    'from_raw',
    'IPASymbol',
]

F = TypeVar('F', bound=Feature)

RelaxedFeatureKind = Union[Type[Feature], str]


class IPASymbol:
    """Parser and feature retriever for standalone symbols/sounds."""

    _string: str
    _features: Optional[FeatureSet]

    _components: Optional[tuple[IPASymbol, ...]]

    @property
    def components(self) -> Optional[tuple[IPASymbol, ...]]:
        """Component symbols of the compound sounds (or None if not a compound sound)."""
        return self._components

    @property
    def left(self) -> Optional[IPASymbol]:
        """The first component of the symbol, if there are any (None otherwise)."""
        return self._components[0] if self._components else None

    @property
    def middle(self) -> Optional[IPASymbol]:
        """The middle component of the symbol, if the number of components is odd (None otherwise)."""
        length = len(self._components or [])
        return self._components[(length - 1) // 2] if length % 2 == 1 else None

    @property
    def right(self) -> Optional[IPASymbol]:
        """The last component of the symbol, if there are any (None otherwise)."""
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
            self._set_raw(symbol.data)
        else:
            self._set_raw(RawSymbol(
                string=data.normalized,
                features=None,
                components=None,
            ))

    @overload
    def features(self) -> Optional[FeatureSet]:
        ...

    @overload
    def features(self, kind: Type[F]) -> Optional[frozenset[F]]:
        ...

    @overload
    def features(self, kinds: Union[set[Type[Feature]], frozenset[Type[Feature]]]) -> Optional[FeatureSet]:
        ...

    def features(self, kinds: Optional[Union[RelaxedFeatureKind,
                                             set[RelaxedFeatureKind],
                                             frozenset[RelaxedFeatureKind]]] = None) -> Optional[FeatureSet]:
        """Retrieve features of the symbol.

        :param kinds: If provided, only the given kind(s) of features are retrieved. For example,
                      s.features(Manner) or s.features({Manner}) will return a set of manners of articulation;
                      s.features({Manner, Place}) will return a combined set of manner(s) and place(s), etc.
                      Strings may be used ('PlaceCategory' or 'place category') instead of the classes with no typing
                      support.
        :return: A (frozen)set of the features.
        :raises:
            FeatureKindError: The value(s) provided are not valid feature kinds.
        """
        if kinds is None:
            return self._features

        def normalize_kind(kind: RelaxedFeatureKind) -> Type[Feature]:
            if isinstance(kind, type) and issubclass(kind, Feature):
                return kind
            if isinstance(kind, str) and (found_kind := find_feature_kind(kind)):
                return found_kind
            raise FeatureKindError(kind)

        kind_index = set(map(normalize_kind, kinds if isinstance(kinds, (set, frozenset)) else {kinds}))
        # After we have verified that the arguments are valid, we can finally check if the symbol is known:
        if self._features is None:
            return None
        return frozenset(feature for feature in self._features if any(isinstance(feature, kind) for kind in kind_index))

    def _set_raw(self, data: RawSymbol) -> None:
        self._string = data.string
        self._features = data.features
        self._components = (tuple(IPASymbol._from_raw(component) for component in data.components)
                            if data.components is not None else None)

    @staticmethod
    def _from_raw(data: RawSymbol) -> IPASymbol:
        symbol = IPASymbol.__new__(IPASymbol)
        symbol._set_raw(data)
        return symbol


from_raw = (
    # So that package-level privacy of _from_raw is maintained
    IPASymbol._from_raw  # noqa
)
