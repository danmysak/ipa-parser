from .feature import Feature

__all__ = [
    'Articulation',
]


class Articulation(Feature):
    APICAL = 'apical'
    LAMINAL = 'laminal'
    ADVANCED = 'advanced'
    RETRACTED = 'retracted'
    CENTRALIZED = 'centralized'
    MID_CENTRALIZED = 'mid-centralized'
    RAISED = 'raised'
    LOWERED = 'lowered'
