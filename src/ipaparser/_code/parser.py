from dataclasses import dataclass
from typing import Optional

from .combiner import apply_position, get_matcher, match_to_feature_sets
from .data import get_data
from .data_types import Symbol
from .definitions import BracketStrategy
from .features import FeatureSet
from .ipa_config import IPAConfig
from .matcher import Match
from .phonetics import combine_feature_sets
from .raw_symbol import RawSymbol
from .strings import (
    combine,
    decompose,
    expand_brackets,
    perform_substitutions,
    StringPositions,
    strip_brackets,
    to_positions,
)

__all__ = [
    'parse',
]


@dataclass(frozen=True)
class Segment:
    start: int
    end: int
    feature_sets: list[FeatureSet]
    components: Optional[list[RawSymbol]] = None


class Parser:
    _positions: StringPositions
    _tie_free: StringPositions
    _total: int
    _all_tied: bool

    def __init__(self, string: str, *, all_tied: bool = False) -> None:
        self._positions = to_positions(string)
        ties = get_data().ties
        self._tie_free = tuple(''.join(character
                                       for index, character in enumerate(position)
                                       if index == 0 or character not in ties)
                               for position in self._positions)
        self._total = len(self._positions)
        self._all_tied = all_tied

    def _extract(self, start: int, end: int, *, omit_final_tie: bool = False) -> str:
        return ''.join((self._tie_free if omit_final_tie and position == end - 1 else self._positions)[position]
                       for position in range(max(start, 0), min(end, self._total)))

    def _is_tied(self, position: int) -> bool:
        return ((self._all_tied and position < self._total - 1)
                or len(self._tie_free[position]) < len(self._positions[position]))

    def _expand(self, segment: Segment, from_position: int, until_position: int) -> Segment:
        feature_sets = segment.feature_sets

        def iterate(initial: int, step: int, final: int) -> int:
            nonlocal feature_sets
            position = initial
            while position != final and (next_feature_sets := apply_position(
                position=self._tie_free[(next_position := position + step)],
                feature_sets=feature_sets,
                is_preceding=step < 0,
            )):
                position = next_position
                feature_sets = next_feature_sets
            return position

        start = iterate(segment.start, -1, from_position)
        end = iterate(segment.end - 1, 1, until_position - 1) + 1
        return Segment(start, end, feature_sets, segment.components)

    def _match(self, start: int, length: Optional[int] = None) -> Optional[Match[Symbol]]:
        return get_matcher().match(self._tie_free, start, length)

    def _get_segment_at(self, start: int) -> Optional[Segment]:
        if match := self._match(start):
            end = start + match.length
            feature_sets = match_to_feature_sets(match)
            for submatch_length in range(match.length - 1, 0, -1):
                for submatch_start in range(start, start + match.length - submatch_length + 1):
                    if submatch := self._match(submatch_start, submatch_length):
                        submatch_end = submatch_start + submatch_length
                        expanded = self._expand(Segment(submatch_start, submatch_end, match_to_feature_sets(submatch)),
                                                start, end)
                        if expanded.start == start and expanded.end == end:
                            feature_sets.extend(expanded.feature_sets)
            return Segment(start, end, feature_sets,
                           components=None if feature_sets else Parser(match.primary_option.data.string).parse())
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
                segments[index + 1].start if index + 1 < len(segments) else self._total,
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
            feature_sets=segment.feature_sets,
            components=segment.components,
        )

    def _tie(self, groups: list[list[Segment]]) -> list[Segment]:
        result: list[Segment] = []
        for group in groups:
            if len(group) > 1:
                feature_sets = [segment.feature_sets for segment in group]
                result.append(Segment(
                    start=group[0].start,
                    end=group[-1].end,
                    feature_sets=combine_feature_sets(*feature_sets),
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
                    collected.append(Segment(end, end + 1, []))
                end = collected[-1].end
            if len(collected) == 1 and not self._is_tied(end - 1):
                symbols.append(self._segment_to_symbol(collected[0]))
            else:
                symbols.append(RawSymbol(
                    string=self._extract(start, end),
                    feature_sets=[],
                    components=[self._segment_to_symbol(segment, is_component=True) for segment in collected],
                ))
            start = end
        return symbols


def normalize(string: str, config: IPAConfig) -> str:
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


def parse(string: str, config: IPAConfig, *, all_tied: bool = False) -> list[RawSymbol]:
    return Parser(normalize(string, config), all_tied=all_tied).parse()
