from ...helpers.enums import StrEnum

__all__ = [
    'Articulation',
]


class Articulation(StrEnum):
    APICAL = 'apical'
    LAMINAL = 'laminal'
    ADVANCED = 'advanced'
    RETRACTED = 'retracted'
    CENTRALIZED = 'centralized'
    MID_CENTRALIZED = 'mid-centralized'
    RAISED = 'raised'
    LOWERED = 'lowered'
