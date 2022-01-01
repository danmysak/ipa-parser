from __future__ import annotations
from itertools import count
from typing import Iterable, Optional
import unicodedata

__all__ = [
    'Match',
    'Matcher',
    'Positions',
]


class Positions:
    positions: list[list[str]]

    def __init__(self, data: list[list[str]]) -> None:
        self.positions = data

    def string(self) -> str:
        return ''.join(''.join(position) for position in self.positions)

    def length(self) -> int:
        return len(self.positions)

    def total(self) -> int:
        return sum(map(len, self.positions))


MatchBuilder = tuple[
    Optional[bool],  # True = matched character, False = unmatched character, None = a new position
    Optional['MatchBuilder'],  # preceding character, if any
]


class Match:
    match: Positions
    extra_diacritics: Positions
    original: Positions

    def __init__(self, string: str, builder: Optional[MatchBuilder]) -> None:
        match: list[list[str]] = []
        extra_diacritics: list[list[str]] = []
        original: list[list[str]] = []

        def build(current: Optional[MatchBuilder]) -> int:  # Returns the number of matched characters
            if current is None:
                return 0
            is_matched, nested = current
            prefix_length = build(nested)
            if is_matched is None:
                match.append([])
                extra_diacritics.append([])
                original.append([])
                return prefix_length
            else:
                updated = [original, match if is_matched else extra_diacritics]
                assert all(updated) and len(string) > prefix_length
                for updated_list in updated:
                    updated_list[-1].append(string[prefix_length])
                return prefix_length + 1

        build(builder)
        self.match = Positions(match)
        self.extra_diacritics = Positions(extra_diacritics)
        self.original = Positions(original)

    def position_count(self) -> int:
        return self.original.length()

    def total_length(self) -> int:
        return self.original.total()


Tree = dict[str, 'Tree']
BranchesWithMatches = list[tuple[Tree, Optional[MatchBuilder]]]


class Trie:
    _tree: Tree
    _LEAF = ''

    def __init__(self, strings: Optional[Iterable[str]] = None) -> None:
        self._tree = {}
        for string in (strings or []):
            self.add(string)

    @staticmethod
    def _is_leaf(node: Tree) -> bool:
        return Trie._LEAF in node

    @staticmethod
    def _make_leaf(node: Tree) -> None:
        node[Trie._LEAF] = node

    def add(self, string: str) -> None:
        node = self._tree
        for character in string:
            if character not in node:
                node[character] = {}
            node = node[character]
        self._make_leaf(node)

    def match(self, string: str, starting_at: int) -> list[Match]:
        branches: BranchesWithMatches = [(self._tree, None)]
        matches: list[Match] = []
        for position in count(starting_at):
            is_last = position == len(string)
            character = string[position] if not is_last else None
            combining_class = unicodedata.combining(character) if character else None
            if is_last or combining_class == 0:
                matches.extend(Match(string, match) for branch, match in branches if self._is_leaf(branch))
            if is_last:
                break
            if combining_class == 0 or position == starting_at:
                branches = [(branch, (None, match)) for branch, match in branches]
            next_branches: BranchesWithMatches = []
            for branch, match in branches:
                if character in branch:
                    next_branches.append((branch[character], (True, match)))
                if combining_class != 0:
                    next_branches.append((branch, (False, match)))
            if not next_branches:
                break
            branches = next_branches
        return matches


class Matcher:
    _trie: Trie

    def __init__(self, strings: Iterable[str]) -> None:
        self._trie = Trie(strings)

    def match(self, string: str, starting_at: int) -> Optional[Match]:
        return (max(matches, key=lambda match: (match.position_count(), -match.extra_diacritics.total()))
                if (matches := self._trie.match(string, starting_at))
                else None)
