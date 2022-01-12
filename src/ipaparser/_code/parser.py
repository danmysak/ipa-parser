from dataclasses import dataclass
from typing import Optional

from .combiner import apply_position, get_matcher, match_to_features
from .data import get_data
from .definitions import BracketStrategy
from .features import FeatureSet
from .ipa_config import IPAConfig
from .phonetics import combine_features
from .raw_symbol import RawSymbol
from .strings import (
    combine,
    decompose,
    expand_brackets,
    perform_substitutions,
    StringPositions,
    strip_brackets,
    to_positions,
    to_string,
)

__all__ = [
    'Parser',
]


@dataclass(frozen=True)
class Segment:
    start: int
    end: int
    features: Optional[FeatureSet] = None
    components: Optional[list[RawSymbol]] = None


class Parser:
    _string: str
    _positions: StringPositions
    _tie_free: StringPositions
    _total: int
    _all_tied: bool

    @property
    def normalized(self) -> str:
        return self._string

    def __init__(self, string: str, config: IPAConfig, *, all_tied: bool = False) -> None:
        self._string = self._normalize(string, config)
        self._positions = to_positions(self._string)
        ties = get_data().ties
        self._tie_free = tuple(''.join(character
                                       for index, character in enumerate(position)
                                       if index == 0 or character not in ties)
                               for position in self._positions)
        self._total = len(self._positions)
        self._all_tied = all_tied

    @staticmethod
    def _normalize(string: str, config: IPAConfig) -> str:
        data = get_data()
        string = decompose(string)
        if config.substitutions:
            string = perform_substitutions(string, data.substitutions)  # first pass
        if config.brackets == BracketStrategy.EXPAND:
            string = expand_brackets(string, data.inner_brackets)
        elif config.brackets == BracketStrategy.STRIP:
            string = strip_brackets(string, data.inner_brackets)
        string = combine(string, config.combined, data.main_tie, data.ties)
        if config.substitutions:
            string = perform_substitutions(string, data.substitutions)  # second pass
        return string

    def _extract(self, start: int, end: int, *, omit_final_tie: bool = False) -> str:
        return ''.join((self._tie_free if omit_final_tie and position == end - 1 else self._positions)[position]
                       for position in range(max(start, 0), min(end, self._total)))

    def _is_tied(self, position: int) -> bool:
        return ((self._all_tied and position < self._total - 1)
                or len(self._tie_free[position]) < len(self._positions[position]))

    def _expand(self, segment: Segment, min_position: int, max_position: int) -> Segment:
        features = segment.features
        if features is None:
            return segment

        def iterate(initial: int, step: int, final: int) -> int:
            nonlocal features
            position = initial
            while position != final and (next_features := apply_position(
                position=self._tie_free[(next_position := position + step)],
                features=features,
                is_preceding=step < 0,
            )) is not None:
                position = next_position
                features = next_features
            return position

        start = iterate(segment.start, -1, min_position)
        end = iterate(segment.end - 1, 1, max_position) + 1
        return Segment(start, end, features, segment.components)

    def _get_segment_at(self, start: int) -> Optional[Segment]:
        if match := get_matcher().match(self._tie_free, start):
            features = match_to_features(match)
            end = start + match.length
            return Segment(start, end, features,
                           components=[RawSymbol(to_string(match.matched), match.data)] if features is None else None)
        else:
            return None

    def _get_initial_segments(self) -> list[Segment]:
        segments: list[Segment] = []
        start = 0
        while start < self._total:
            if segment := self._get_segment_at(start):
                segments.append(segment)
                assert segment.end > start
                start = segment.end
            else:
                start += 1
        return segments

    def _expand_all(self, segments: list[Segment]) -> list[Segment]:
        expanded: list[Segment] = []
        for index, segment in enumerate(segments):
            expanded.append(self._expand(
                segment,
                expanded[index - 1].end if index > 0 else 0,
                (segments[index + 1].start if index + 1 < len(segments) else self._total) - 1,
            ))
        return expanded

    def _group(self, segments: list[Segment]) -> list[list[Segment]]:
        groups: list[list[Segment]] = []
        last: Optional[Segment] = None
        for segment in segments:
            if last and segment.start == last.end and self._is_tied(segment.start - 1):
                groups[-1].append(segment)
            else:
                groups.append([segment])
            last = segment
        return groups

    def _segment_to_symbol(self, segment: Segment, *, is_component: bool = False) -> RawSymbol:
        return RawSymbol(
            string=self._extract(segment.start, segment.end, omit_final_tie=is_component),
            features=segment.features,
            components=segment.components,
        )

    def _tie(self, groups: list[list[Segment]]) -> list[Segment]:
        result: list[Segment] = []
        for group in groups:
            if len(group) > 1:
                feature_sets = [segment.features for segment in group]
                result.append(Segment(
                    start=group[0].start,
                    end=group[-1].end,
                    features=combine_features(feature_sets) if None not in feature_sets else None,
                    components=[self._segment_to_symbol(segment, is_component=True) for segment in group],
                ))
            else:
                result.append(group[0])
        return result

    def parse(self) -> list[RawSymbol]:
        symbols: list[RawSymbol] = []
        segments = self._expand_all(self._tie(self._group(self._expand_all(self._get_initial_segments()))))
        start = 0
        next_segment = 0
        while start < self._total:
            collected: list[Segment] = []
            end = start
            while end < self._total and (end == start or self._is_tied(end - 1)):
                if next_segment < len(segments) and end == segments[next_segment].start:
                    collected.append(segments[next_segment])
                    next_segment += 1
                else:
                    collected.append(Segment(end, end + 1))
                end = collected[-1].end
            if len(collected) == 1 and not self._is_tied(end - 1):
                symbols.append(self._segment_to_symbol(collected[0]))
            else:
                symbols.append(RawSymbol(
                    string=self._extract(start, end),
                    components=[self._segment_to_symbol(segment, is_component=True) for segment in collected],
                ))
            start = end
        return symbols
