from typing import Any

__all__ = [
    'FeatureKindError',
]


class FeatureKindError(ValueError):
    value: str

    def __init__(self, value: Any) -> None:
        super().__init__(f'Invalid feature kind: {repr(value)}')
        self.value = value
