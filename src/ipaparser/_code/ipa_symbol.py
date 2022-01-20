from __future__ import annotations
from typing import Any, Optional, overload, Type, TypeVar, Union

from .exceptions import FeatureError, FeatureKindError
from .feature_helper import find_feature, find_feature_kind, include
from .features import Feature, FeatureKind, FeatureSet, SymbolType
from .ipa_config import IPAConfig
from .parser import parse
from .raw_symbol import RawSymbol

__all__ = [
    'from_raw',
    'IPASymbol',
]

F = TypeVar('F', bound=Feature)

RelaxedFeature = Union[Feature, str]
RelaxedFeatureKind = Union[FeatureKind, str]


class IPASymbol:
    """Parser and feature retriever for standalone symbols/sounds."""

    _string: str
    _feature_sets: list[FeatureSet]

    _components: Optional[tuple[IPASymbol, ...]]

    @property
    def components(self) -> Optional[tuple[IPASymbol, ...]]:
        """
        If the symbol is either a known or an unknown compound: component symbols left to right;
        if the symbol is an unknown combination of a base symbol and combining mark(s): the base symbol;
        otherwise: None.
        """
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

    def __eq__(self, other: Any) -> bool:
        return str(self) == str(other) if isinstance(other, (IPASymbol, str)) else NotImplemented

    def __hash__(self) -> int:
        return hash(str(self))  # str instead of repr is required to be compatible with __eq__

    def __bool__(self) -> bool:
        return bool(str(self))

    def __init__(self, string: str, config: IPAConfig = IPAConfig()) -> None:
        """Parse a single sound or auxiliary IPA symbol.

        :param string: The string to parse (like 'a', 'pʰ', '˦', or 'ˈˈ').
        :param config: Parsing parameters.
        """
        self._set_raw(symbols[0]
                      if (symbols := parse(string, config, all_tied=True))
                      else RawSymbol(string, []))

    def as_string(self) -> str:
        """Return the symbol's underlying (normalized) string."""
        return str(self)

    @staticmethod
    def _check_normalize_kind(kind: RelaxedFeatureKind) -> FeatureKind:
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
    def features(self, kinds: Union[set[FeatureKind], frozenset[FeatureKind]],
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
                      Strings may be used ('PlaceCategory' or 'place category') instead of Feature subclasses (with
                      no typing support).
        :param role: If provided, the symbol's feature set may be reinterpreted (see below) so that the returned set is
                     guaranteed to be consistent with `role`: to contain `role` before being filtered by `kinds`. If
                     the symbol does not have the feature and cannot be reinterpreted to have it, None will be returned.
                     Currently, the reinterpretations supported are:
                     1) nonsyllabic front/back close vowels as palatal/velar approximants;
                     2) "ambiguous" alveolar consonants (t, n, ǁ, etc.) as dental or as postalveolar;
                     3) ad-hoc combinations (e.g., ä ~ central vowel) as literal ones (ä ~ centralized front vowel).
                     Strings may be used ('consonant') instead of Feature subclass values (with no typing support).
        :return: A (frozen)set of the features or None for unknown symbols and symbols with an incompatible `role`.
        :raises:
            FeatureKindError: The value(s) of the `kinds` parameter are not valid feature kinds.
            FeatureError: The value of the `role` parameter is not a valid feature.
        """
        kind_index: Optional[set[FeatureKind]] = (
            set(map(self._check_normalize_kind, kinds if isinstance(kinds, (set, frozenset)) else {kinds}))
            if kinds is not None else None
        )
        required_features: set[Feature] = {self._check_normalize_feature(role)} if role is not None else set()
        return next(
            (
                include(kind_index, features) if kind_index is not None else features
                for features in self._feature_sets
                if features >= required_features
            ),
            None
        )

    def is_known(self) -> bool:
        """Whether the symbol has a set of associated features."""
        return len(self._feature_sets) > 0

    @overload
    def has_feature(self, feature: Feature) -> bool:
        ...

    def has_feature(self, feature: RelaxedFeature) -> bool:
        """
        Whether the symbol is known and has a given feature; strings may be used ('consonant') instead of Feature
        subclass values (with no typing support).
        """
        return bool(self._feature_sets) and self._check_normalize_feature(feature) in self._feature_sets[0]

    def is_sound(self) -> bool:
        """Whether the symbol is a known sound."""
        return self.has_feature(SymbolType.SOUND)

    def is_break(self) -> bool:
        """Whether the symbol is a known break."""
        return self.has_feature(SymbolType.BREAK)

    def is_suprasegmental(self) -> bool:
        """Whether the symbol is a known suprasegmental."""
        return self.has_feature(SymbolType.SUPRASEGMENTAL)

    def _set_raw(self, data: RawSymbol) -> None:
        self._string = data.string
        self._feature_sets = data.feature_sets
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
