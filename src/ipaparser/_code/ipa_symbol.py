from __future__ import annotations
from typing import Optional, overload, Type, TypeVar, Union

from .exceptions import FeatureError, FeatureKindError
from .feature_helper import filter_features, find_feature, find_feature_kind
from .features import Feature, FeatureSet
from .ipa_config import IPAConfig
from .parser import parse
from .phonetics import interpret
from .raw_symbol import RawSymbol

__all__ = [
    'from_raw',
    'IPASymbol',
]

F = TypeVar('F', bound=Feature)

RelaxedFeature = Union[Feature, str]
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
            self._set_raw(RawSymbol(data.normalized))

    @staticmethod
    def _check_normalize_kind(kind: RelaxedFeatureKind) -> Type[Feature]:
        if isinstance(kind, type) and issubclass(kind, Feature):
            return kind
        if isinstance(kind, str) and (found_kind := find_feature_kind(kind)):
            return found_kind
        raise FeatureKindError(kind)

    @staticmethod
    def _check_normalize_feature(feature: RelaxedFeature) -> Feature:
        if isinstance(feature, Feature):
            return feature
        if isinstance(feature, str) and (found_feature := find_feature(feature)):
            return found_feature
        raise FeatureError(feature)

    @overload
    def features(self, *, role: Optional[Feature] = None) -> Optional[FeatureSet]:
        ...

    @overload
    def features(self, kind: Type[F], *, role: Optional[Feature] = None) -> Optional[frozenset[F]]:
        ...

    @overload
    def features(self, kinds: Union[set[Type[Feature]], frozenset[Type[Feature]]],
                 *, role: Optional[Feature] = None) -> Optional[FeatureSet]:
        ...

    def features(
            self,
            kinds: Optional[Union[RelaxedFeatureKind, set[RelaxedFeatureKind], frozenset[RelaxedFeatureKind]]] = None,
            *,
            role: Optional[RelaxedFeature] = None,
    ) -> Optional[FeatureSet]:
        """Retrieve features of the symbol.

        :param kinds: If provided, only the given kind(s) of features are retrieved. For example,
                      s.features(Manner) or s.features({Manner}) will return a set of manners of articulation;
                      s.features({Manner, Place}) will return a combined set of manner(s) and place(s), etc.
                      Strings may be used ('PlaceCategory' or 'place category') instead of Feature subclasses with
                      no typing support.
        :param role: If provided, the returned feature set is guaranteed to be consistent with this feature (that is, to
                     contain this feature before being filtered by `kinds`); if the symbol does not have this feature
                     and cannot be reinterpreted to have this feature, None will be returned.
                     Currently, the only reinterpretations supported are nonsyllabic close vowels as palatal/velar
                     approximants and vice versa.
                     Strings may be used ('consonant') instead of Feature subclass values with no typing support.
        :return: A (frozen)set of the features or None for unknown symbols and symbols with an incompatible `role`.
        :raises:
            FeatureKindError: The value(s) of the `kinds` parameter are not valid feature kinds.
            FeatureError: The value of the `role` parameter is not a valid feature.
        """
        kind_index: Optional[set[Type[Feature]]] = (
            set(map(self._check_normalize_kind, kinds if isinstance(kinds, (set, frozenset)) else {kinds}))
            if kinds is not None else None
        )
        required_features: set[Feature] = {self._check_normalize_feature(role)} if role is not None else set()
        return next(
            (
                filter_features(features, kind_index) if kind_index is not None else features
                for features in interpret(self._features)
                if features >= required_features
            ),
            None
        ) if self._features is not None else None

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
