from .feature import Feature
from .suprasegmental import SuprasegmentalType

__all__ = [
    'Tone',
    'ToneLetter',
    'ToneNumber',
    'ToneStep',
    'ToneType',
]


class Tone(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Pitch_and_tone
    """

    EXTRA_HIGH_TONE = 'extra-high tone'
    HIGH_TONE = 'high tone'
    MID_TONE = 'mid tone'
    LOW_TONE = 'low tone'
    EXTRA_LOW_TONE = 'extra-low tone'

    RISING_TONE = 'rising tone'
    FALLING_TONE = 'falling tone'
    HIGH_MID_RISING_TONE = 'high/mid rising tone'
    LOW_RISING_TONE = 'low rising tone'
    HIGH_FALLING_TONE = 'high falling tone'
    LOW_MID_FALLING_TONE = 'low/mid falling tone'
    PEAKING_TONE = 'peaking tone'
    DIPPING_TONE = 'dipping tone'


class ToneType(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals
    https://en.wikipedia.org/wiki/Tone_number
    https://en.wiktionary.org/wiki/Template:IPA
    """

    TONE_LETTER = 'tone letter'
    TONE_NUMBER = 'tone number'
    TONE_STEP = 'tone step'

    def derived(self) -> SuprasegmentalType:
        return SuprasegmentalType.TONE


class ToneLetter(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals
    """

    HIGH_TONE_LETTER = 'high tone letter'
    HALF_HIGH_TONE_LETTER = 'half-high tone letter'
    MID_TONE_LETTER = 'mid tone letter'
    HALF_LOW_TONE_LETTER = 'half-low tone letter'
    LOW_TONE_LETTER = 'low tone letter'

    def derived(self) -> ToneType:
        return ToneType.TONE_LETTER


class ToneNumber(Feature):
    """
    https://en.wikipedia.org/wiki/Tone_number
    https://en.wiktionary.org/wiki/Template:IPA
    """

    TONE_0 = 'tone 0'
    TONE_1 = 'tone 1'
    TONE_2 = 'tone 2'
    TONE_3 = 'tone 3'
    TONE_4 = 'tone 4'
    TONE_5 = 'tone 5'
    TONE_6 = 'tone 6'
    TONE_7 = 'tone 7'
    TONE_NUMBER_SEPARATOR = 'tone number separator'

    def derived(self) -> ToneType:
        return ToneType.TONE_NUMBER


class ToneStep(Feature):
    """
    https://en.wikipedia.org/wiki/International_Phonetic_Alphabet#Suprasegmentals
    """

    UPSTEP = 'upstep'
    DOWNSTEP = 'downstep'

    def derived(self) -> ToneType:
        return ToneType.TONE_STEP
