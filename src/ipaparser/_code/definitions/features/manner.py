from __future__ import annotations

from .feature import Feature

__all__ = [
    'Manner',
]


class Manner(Feature):
    AFFRICATE = 'affricate'
    APPROXIMANT = 'approximant'
    FRICATIVE = 'fricative'
    LATERAL = 'lateral'
    NASAL = 'nasal'
    SIBILANT = 'sibilant'
    STOP = 'stop'
    TAP_FLAP = 'tap/flap'
    TRILL = 'trill'

    CLICK = 'click'
    EJECTIVE = 'ejective'
    IMPLOSIVE = 'implosive'
