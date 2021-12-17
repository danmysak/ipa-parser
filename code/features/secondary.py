from ..helpers.enums import StrEnum

__all__ = [
    'SecondaryModifier',
    'SecondaryPlace',
]


class SecondaryPlace(StrEnum):
    LABIALIZED = 'labialized'
    PALATALIZED = 'palatalized'
    VELARIZED = 'velarized'
    PHARYNGEALIZED = 'pharyngealized'
    GLOTTALIZED = 'glottalized'


class SecondaryModifier(StrEnum):
    ADVANCED_TONGUE_ROOT = 'advanced tongue root'
    RETRACTED_TONGUE_ROOT = 'retracted tongue root'
    RHOTIC = 'rhotic'
    NASALIZED = 'nasalized'
    PRENASALIZED = 'prenasalized'
    PRESTOPPED = 'prestopped'
