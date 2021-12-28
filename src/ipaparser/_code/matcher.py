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

    def __init__(self, base: Optional[list[list[str]]] = None) -> None:
        self.positions = [] if base is None else base

    def extend(self) -> Positions:
        return Positions(self.positions + [[]])

    def append(self, character: str) -> Positions:
        if not self.positions:
            raise ValueError('Cannot append to the last position of an empty list')
        return Positions(self.positions[:-1] + [self.positions[-1] + [character]])

    def string(self) -> str:
        return ''.join(''.join(position) for position in self.positions)

    def length(self) -> int:
        return len(self.positions)

    def total(self) -> int:
        return len(self.string())


class Match:
    match: Positions
    extra_diacritics: Positions
    original: Positions

    def __init__(self, base: Optional[Match] = None, *, append: Optional[str] = None, matched: bool = True) -> None:
        if base is None:
            self.match = Positions()
            self.extra_diacritics = Positions()
            self.original = Positions()
        elif append is None:
            self.match = base.match.extend()
            self.extra_diacritics = base.extra_diacritics.extend()
            self.original = base.original.extend()
        else:
            self.match = base.match.append(append) if matched else base.match
            self.extra_diacritics = base.extra_diacritics.append(append) if not matched else base.extra_diacritics
            self.original = base.original.append(append)

    def matched(self) -> str:
        return self.match.string()

    def position_count(self) -> int:
        return self.original.length()

    def total_length(self) -> int:
        return self.original.total()

    def total_extra_diacritics(self) -> int:
        return self.extra_diacritics.total()


Tree = dict[str, 'Tree']
BranchesWithMatches = list[tuple[Tree, Match]]


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
        branches: BranchesWithMatches = [(self._tree, Match())]
        matches: list[Match] = []
        for position in count(starting_at):
            is_last = position == len(string)
            character = string[position] if not is_last else None
            combining_class = unicodedata.combining(character) if character else None
            if is_last or combining_class == 0:
                matches.extend(match for branch, match in branches if self._is_leaf(branch))
            if is_last:
                break
            if combining_class == 0 or position == starting_at:
                branches = [(branch, Match(match)) for branch, match in branches]
            next_branches: BranchesWithMatches = []
            for branch, match in branches:
                if character in branch:
                    next_branches.append((branch[character], Match(match, append=character, matched=True)))
                if combining_class != 0:
                    next_branches.append((branch, Match(match, append=character, matched=False)))
            if not next_branches:
                break
            branches = next_branches
        return matches


class Matcher:
    _trie: Trie

    def __init__(self, strings: Iterable[str]) -> None:
        self._trie = Trie(strings)

    def match(self, string: str, starting_at: int) -> Optional[Match]:
        return (max(matches, key=lambda match: (match.position_count(), -match.total_extra_diacritics()))
                if (matches := self._trie.match(string, starting_at))
                else None)
