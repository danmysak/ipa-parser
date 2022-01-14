from .airflow import Airflow
from .articulation import Articulation
from .aspiration import Aspiration
from .backness import Backness, BacknessCategory
from .breaks import BreakType
from .feature import Feature, FeatureKind, FeatureSet
from .height import Height, HeightCategory
from .intonation import Intonation
from .length import Length
from .manner import Manner
from .place import Place, PlaceCategory
from .release import Release
from .roundedness import Roundedness, RoundednessModifier
from .secondary import SecondaryModifier, SecondaryPlace
from .sound import SoundSubtype, SoundType
from .strength import Strength
from .stress import StressSubtype, StressType
from .suprasegmental import SuprasegmentalType
from .syllabicity import Syllabicity
from .symbol import SymbolType
from .tone import Tone, ToneLetter, ToneNumber, ToneStep, ToneType
from .voice import Phonation, Voicing

__all__ = [
    'Airflow',
    'Articulation',
    'Aspiration',
    'Backness',
    'BacknessCategory',
    'BreakType',
    'Feature',
    'FEATURE_KINDS',
    'FeatureKind',
    'FeatureSet',
    'Height',
    'HeightCategory',
    'Intonation',
    'Length',
    'Manner',
    'Phonation',
    'Place',
    'PlaceCategory',
    'Release',
    'Roundedness',
    'RoundednessModifier',
    'SecondaryModifier',
    'SecondaryPlace',
    'SoundSubtype',
    'SoundType',
    'Strength',
    'StressSubtype',
    'StressType',
    'SuprasegmentalType',
    'Syllabicity',
    'SymbolType',
    'Tone',
    'ToneLetter',
    'ToneNumber',
    'ToneStep',
    'ToneType',
    'Voicing',
]

FEATURE_KINDS: tuple[FeatureKind, ...] = tuple(value for name in __all__
                                               if (value := globals().get(name, None))
                                               and isinstance(value, type)
                                               and issubclass(value, Feature)
                                               and value != Feature)
