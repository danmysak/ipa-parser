from .feature import assert_feature_mapping, Feature

__all__ = [
    'Backness',
    'BacknessCategory',
]


class BacknessCategory(Feature):
    ABOUT_FRONT = 'about front'
    ABOUT_CENTRAL = 'about central'
    ABOUT_BACK = 'about back'


class Backness(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Vowels
    """

    FRONT = 'front'
    NEAR_FRONT = 'near-front'
    CENTRAL = 'central'
    NEAR_BACK = 'near-back'
    BACK = 'back'

    def derived(self) -> BacknessCategory:
        return BACKNESS_TO_CATEGORY[self]


BACKNESS_TO_CATEGORY = assert_feature_mapping({
    Backness.FRONT: BacknessCategory.ABOUT_FRONT,
    Backness.NEAR_FRONT: BacknessCategory.ABOUT_FRONT,
    Backness.CENTRAL: BacknessCategory.ABOUT_CENTRAL,
    Backness.NEAR_BACK: BacknessCategory.ABOUT_BACK,
    Backness.BACK: BacknessCategory.ABOUT_BACK,
})
