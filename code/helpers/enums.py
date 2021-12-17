from enum import Enum
from typing import Any, TypeVar

__all__ = [
    'assert_enum_mapping',
    'StrEnum',
]


class StrEnum(str, Enum):
    pass


M = TypeVar('M', bound=dict[StrEnum, Any])


def assert_enum_mapping(mapping: M) -> M:
    assert mapping and set(mapping.keys()) == set(type(next(iter(mapping.keys()))))
    return mapping
