from ..helpers.enums import StrEnum

__all__ = [
    'Length',
]


class Length(StrEnum):
    ANAPTYCTIC = 'anaptyctic'
    EXTRA_SHORT = 'extra-short'
    HALF_LONG = 'half-long'
    LONG = 'long'
    EXTRA_LONG = 'extra-long'
