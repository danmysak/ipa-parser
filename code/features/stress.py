from ..helpers.enums import assert_enum_mapping, StrEnum

__all__ = [
    'StressSubtype',
    'StressType',
]


class StressType(StrEnum):
    PRIMARY_STRESS = 'primary stress'
    SECONDARY_STRESS = 'secondary stress'


class StressSubtype(StrEnum):
    REGULAR_PRIMARY_STRESS = 'regular primary stress'
    EXTRA_STRONG_PRIMARY_STRESS = 'extra-strong primary stress'
    REGULAR_SECONDARY_STRESS = 'regular secondary stress'
    EXTRA_WEAK_SECONDARY_STRESS = 'extra-weak secondary stress'

    def to_stress_type(self) -> StressType:
        return STRESS_SUBTYPE_TO_TYPE[self]


STRESS_SUBTYPE_TO_TYPE = assert_enum_mapping({
    StressSubtype.REGULAR_PRIMARY_STRESS: StressType.PRIMARY_STRESS,
    StressSubtype.EXTRA_STRONG_PRIMARY_STRESS: StressType.PRIMARY_STRESS,
    StressSubtype.REGULAR_SECONDARY_STRESS: StressType.SECONDARY_STRESS,
    StressSubtype.EXTRA_WEAK_SECONDARY_STRESS: StressType.SECONDARY_STRESS,
})
