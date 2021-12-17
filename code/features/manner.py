from __future__ import annotations

from ..helpers.enums import StrEnum

__all__ = [
    'DEFAULT_MECHANISM',
    'Manner',
    'Mechanism',
]


class Manner(StrEnum):
    APPROXIMANT = 'approximant'
    FRICATIVE = 'fricative'
    LATERAL = 'lateral'
    NASAL = 'nasal'
    SIBILANT = 'sibilant'
    STOP = 'stop'
    TAP_FLAP = 'tap/flap'
    TRILL = 'trill'


class Mechanism(StrEnum):
    CLICK = 'click'
    EJECTIVE = 'ejective'
    IMPLOSIVE = 'implosive'
    PULMONIC = 'pulmonic'


DEFAULT_MECHANISM = Mechanism.PULMONIC
