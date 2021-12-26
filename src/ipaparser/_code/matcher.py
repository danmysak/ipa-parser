from dataclasses import dataclass
from itertools import count
from typing import Iterable, Optional
import unicodedata

__all__ = [
    'Match',
    'Matcher',
]


@dataclass(frozen=True)
class Match:
    string: str
    extra_diacritics_by_position: list[list[str]]

    def position_count(self) -> int:
        return len(self.extra_diacritics_by_position)

    def total_extra_diacritics(self) -> int:
        return sum(map(len, self.extra_diacritics_by_position))

    def total_length(self) -> int:
        return len(self.string) + self.total_extra_diacritics()


Tree = dict[str, 'Tree']
BranchesWithMatches = list[tuple[Tree, Match]]


def with_appended(data: list[list[str]], item: str) -> list[list[str]]:
    return data[:-1] + [data[-1] + [item]]


class Trie:
    _tree: Tree
    _LEAF = ''

    def __init__(self, strings: Optional[Iterable[str]] = None):
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
        branches: BranchesWithMatches = [(self._tree, Match(
            string='',
            extra_diacritics_by_position=[],
        ))]
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
                branches = [(branch, Match(
                    string=match.string,
                    extra_diacritics_by_position=match.extra_diacritics_by_position + [[]],
                )) for branch, match in branches]
            next_branches: BranchesWithMatches = []
            for branch, match in branches:
                if character in branch:
                    next_branches.append((branch[character], Match(
                        string=match.string + character,
                        extra_diacritics_by_position=match.extra_diacritics_by_position,
                    )))
                if combining_class != 0:
                    next_branches.append((branch, Match(
                        string=match.string,
                        extra_diacritics_by_position=with_appended(match.extra_diacritics_by_position, character),
                    )))
            if not next_branches:
                break
            branches = next_branches
        return matches


class Matcher:
    _trie: Trie

    def __init__(self, strings: Iterable[str]):
        self._trie = Trie(strings)

    def match(self, string: str, starting_at: int) -> Optional[Match]:
        return (max(matches, key=lambda match: (match.position_count(), -match.total_extra_diacritics()))
                if (matches := self._trie.match(string, starting_at))
                else None)
