from .feature import Feature

__all__ = [
    'Tone',
    'ToneNumber',
    'ToneStep',
    'ToneType',
]


class ToneType(Feature):
    TONE_DESCRIPTION = 'tone description'
    TONE_NUMBER = 'tone number'
    TONE_STEP = 'tone step'


class Tone(Feature):
    EXTRA_HIGH_TONE = 'extra-high tone'
    HIGH_TONE = 'high tone'
    HALF_HIGH_TONE = 'half-high tone'
    MID_TONE = 'mid tone'
    HALF_LOW_TONE = 'half-low tone'
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


class ToneNumber(Feature):
    TONE_0 = 'tone 0'
    TONE_1 = 'tone 1'
    TONE_2 = 'tone 2'
    TONE_3 = 'tone 3'
    TONE_4 = 'tone 4'
    TONE_5 = 'tone 5'
    TONE_6 = 'tone 6'
    TONE_7 = 'tone 7'
    TONE_NUMBER_SEPARATOR = 'tone number separator'


class ToneStep(Feature):
    UPSTEP = 'upstep'
    DOWNSTEP = 'downstep'
