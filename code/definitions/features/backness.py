from ...helpers.enums import assert_enum_mapping, StrEnum

__all__ = [
    'Backness',
    'BacknessCategory',
]


class BacknessCategory(StrEnum):
    ABOUT_FRONT = 'about front'
    ABOUT_CENTRAL = 'about central'
    ABOUT_BACK = 'about back'


class Backness(StrEnum):
    FRONT = 'front'
    NEAR_FRONT = 'near-front'
    CENTRAL = 'central'
    NEAR_BACK = 'near-back'
    BACK = 'back'

    def to_backness_category(self) -> BacknessCategory:
        return BACKNESS_TO_CATEGORY[self]


BACKNESS_TO_CATEGORY = assert_enum_mapping({
    Backness.FRONT: BacknessCategory.ABOUT_FRONT,
    Backness.NEAR_FRONT: BacknessCategory.ABOUT_FRONT,
    Backness.CENTRAL: BacknessCategory.ABOUT_CENTRAL,
    Backness.NEAR_BACK: BacknessCategory.ABOUT_BACK,
    Backness.BACK: BacknessCategory.ABOUT_BACK,
})
