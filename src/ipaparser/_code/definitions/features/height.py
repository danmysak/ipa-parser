from ...helpers.enums import assert_enum_mapping, StrEnum

__all__ = [
    'Height',
    'HeightCategory',
]


class HeightCategory(StrEnum):
    ABOUT_CLOSE = 'about close'
    ABOUT_MID = 'about mid'
    ABOUT_OPEN = 'about open'


class Height(StrEnum):
    CLOSE = 'close'
    NEAR_CLOSE = 'near-close'
    CLOSE_MID = 'close-mid'
    MID = 'mid'
    OPEN_MID = 'open-mid'
    NEAR_OPEN = 'near-open'
    OPEN = 'open'

    def to_height_category(self) -> HeightCategory:
        return HEIGHT_TO_CATEGORY[self]


HEIGHT_TO_CATEGORY = assert_enum_mapping({
    Height.CLOSE: HeightCategory.ABOUT_CLOSE,
    Height.NEAR_CLOSE: HeightCategory.ABOUT_CLOSE,
    Height.CLOSE_MID: HeightCategory.ABOUT_MID,
    Height.MID: HeightCategory.ABOUT_MID,
    Height.OPEN_MID: HeightCategory.ABOUT_MID,
    Height.NEAR_OPEN: HeightCategory.ABOUT_OPEN,
    Height.OPEN: HeightCategory.ABOUT_OPEN,
})
