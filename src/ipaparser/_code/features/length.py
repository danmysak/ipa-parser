from .feature import Feature

__all__ = [
    'Length',
]


class Length(Feature):
    """
    https://en.wikipedia.org/wiki/Length_(phonetics)
    """

    EXTRA_SHORT = 'extra-short'
    HALF_LONG = 'half-long'
    LONG = 'long'
    EXTRA_LONG = 'extra-long'
