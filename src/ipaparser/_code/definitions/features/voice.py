from ...helpers.enums import StrEnum

__all__ = [
    'Phonation',
    'Voicing',
]


class Voicing(StrEnum):
    VOICED = 'voiced'


class Phonation(StrEnum):
    BREATHY = 'breathy'
    CREAKY = 'creaky'
    WHISPERY = 'whispery'
