from .feature import assert_feature_mapping, Feature

__all__ = [
    'Place',
    'PlaceCategory',
]


class PlaceCategory(Feature):
    LABIAL = 'labial'
    CORONAL = 'coronal'
    DORSAL = 'dorsal'
    LARYNGEAL = 'laryngeal'


class Place(Feature):
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


PLACE_TO_CATEGORY = assert_feature_mapping({
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
