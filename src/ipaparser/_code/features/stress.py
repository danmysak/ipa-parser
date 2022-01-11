from .feature import assert_feature_mapping, Feature
from .suprasegmental import SuprasegmentalType

__all__ = [
    'StressSubtype',
    'StressType',
]


class StressType(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Stress
    """

    PRIMARY_STRESS = 'primary stress'
    SECONDARY_STRESS = 'secondary stress'

    def derived(self) -> SuprasegmentalType:
        return SuprasegmentalType.STRESS


class StressSubtype(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Stress
    """

    REGULAR_PRIMARY_STRESS = 'regular primary stress'
    EXTRA_STRONG_PRIMARY_STRESS = 'extra-strong primary stress'
    REGULAR_SECONDARY_STRESS = 'regular secondary stress'
    EXTRA_WEAK_SECONDARY_STRESS = 'extra-weak secondary stress'

    def derived(self) -> StressType:
        return STRESS_SUBTYPE_TO_TYPE[self]


STRESS_SUBTYPE_TO_TYPE = assert_feature_mapping({
    StressSubtype.REGULAR_PRIMARY_STRESS: StressType.PRIMARY_STRESS,
    StressSubtype.EXTRA_STRONG_PRIMARY_STRESS: StressType.PRIMARY_STRESS,
    StressSubtype.REGULAR_SECONDARY_STRESS: StressType.SECONDARY_STRESS,
    StressSubtype.EXTRA_WEAK_SECONDARY_STRESS: StressType.SECONDARY_STRESS,
})
