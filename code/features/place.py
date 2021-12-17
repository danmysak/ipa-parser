from ..helpers.enums import assert_enum_mapping, StrEnum

__all__ = [
    'Place',
    'PlaceCategory',
]


class PlaceCategory(StrEnum):
    LABIAL = 'labial'
    CORONAL = 'coronal'
    DORSAL = 'dorsal'
    LARYNGEAL = 'laryngeal'


class Place(StrEnum):
    BILABIAL = 'bilabial'
    LABIODENTAL = 'labiodental'
    LINGUOLABIAL = 'linguolabial'
    DENTAL = 'dental'
    ALVEOLAR = 'alveolar'
    POSTALVEOLAR = 'postalveolar'
    RETROFLEX = 'retroflex'
    PALATAL = 'palatal'
    VELAR = 'velar'
    UVULAR = 'uvular'
    PHARYNGEAL_EPIGLOTTAL = 'pharyngeal/epiglottal'
    GLOTTAL = 'glottal'

    def to_place_category(self) -> PlaceCategory:
        return PLACE_TO_CATEGORY[self]


PLACE_TO_CATEGORY = assert_enum_mapping({
    Place.BILABIAL: PlaceCategory.LABIAL,
    Place.LABIODENTAL: PlaceCategory.LABIAL,
    Place.LINGUOLABIAL: PlaceCategory.CORONAL,
    Place.DENTAL: PlaceCategory.CORONAL,
    Place.ALVEOLAR: PlaceCategory.CORONAL,
    Place.POSTALVEOLAR: PlaceCategory.CORONAL,
    Place.RETROFLEX: PlaceCategory.CORONAL,
    Place.PALATAL: PlaceCategory.DORSAL,
    Place.VELAR: PlaceCategory.DORSAL,
    Place.UVULAR: PlaceCategory.DORSAL,
    Place.PHARYNGEAL_EPIGLOTTAL: PlaceCategory.LARYNGEAL,
    Place.GLOTTAL: PlaceCategory.LARYNGEAL,
})
