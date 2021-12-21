from .feature import Feature

__all__ = [
    'Release',
]


class Release(Feature):
    NO_AUDIBLE_RELEASE = 'no audible release'
    NASAL_RELEASE = 'nasal release'
    LATERAL_RELEASE = 'lateral release'
    VOICELESS_DENTAL_FRICATIVE_RELEASE = 'voiceless dental fricative release'
    VOICELESS_ALVEOLAR_SIBILANT_FRICATIVE_RELEASE = 'voiceless alveolar sibilant fricative release'
    VOICELESS_VELAR_FRICATIVE_RELEASE = 'voiceless velar fricative release'
