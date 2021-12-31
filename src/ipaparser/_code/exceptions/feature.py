from typing import Any

__all__ = [
    'FeatureError',
]


class FeatureError(ValueError):
    value: str

    def __init__(self, value: Any) -> None:
        super().__init__(f'Invalid feature: {repr(value)}')
        self.value = value
