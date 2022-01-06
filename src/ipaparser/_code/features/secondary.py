from .feature import Feature

__all__ = [
    'SecondaryModifier',
    'SecondaryPlace',
]


class SecondaryPlace(Feature):
    LABIALIZED = 'labialized'
    PALATALIZED = 'palatalized'
    VELARIZED = 'velarized'
    PHARYNGEALIZED = 'pharyngealized'
    GLOTTALIZED = 'glottalized'


class SecondaryModifier(Feature):
    ADVANCED_TONGUE_ROOT = 'advanced tongue root'
    RETRACTED_TONGUE_ROOT = 'retracted tongue root'
    R_COLORED = 'r-colored'
    NASALIZED = 'nasalized'
    PRENASALIZED = 'prenasalized'
    VOICELESSLY_PRENASALIZED = 'voicelessly prenasalized'
    PRESTOPPED = 'prestopped'
    PREGLOTTALIZED = 'preglottalized'
