from .feature import Feature

__all__ = [
    'Phonation',
    'Voicing',
]


class Voicing(Feature):
    VOICED = 'voiced'
    DEVOICED = 'devoiced'


class Phonation(Feature):
    BREATHY = 'breathy'
    CREAKY = 'creaky'
    WHISPERY = 'whispery'
