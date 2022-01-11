from .feature import assert_feature_mapping, Feature

__all__ = [
    'Height',
    'HeightCategory',
]


class HeightCategory(Feature):
    ABOUT_CLOSE = 'about close'
    ABOUT_MID = 'about mid'
    ABOUT_OPEN = 'about open'


class Height(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Vowels
    """

    CLOSE = 'close'
    NEAR_CLOSE = 'near-close'
    CLOSE_MID = 'close-mid'
    MID = 'mid'
    OPEN_MID = 'open-mid'
    NEAR_OPEN = 'near-open'
    OPEN = 'open'

    def derived(self) -> HeightCategory:
        return HEIGHT_TO_CATEGORY[self]


HEIGHT_TO_CATEGORY = assert_feature_mapping({
    Height.CLOSE: HeightCategory.ABOUT_CLOSE,
    Height.NEAR_CLOSE: HeightCategory.ABOUT_CLOSE,
    Height.CLOSE_MID: HeightCategory.ABOUT_MID,
    Height.MID: HeightCategory.ABOUT_MID,
    Height.OPEN_MID: HeightCategory.ABOUT_MID,
    Height.NEAR_OPEN: HeightCategory.ABOUT_OPEN,
    Height.OPEN: HeightCategory.ABOUT_OPEN,
})
