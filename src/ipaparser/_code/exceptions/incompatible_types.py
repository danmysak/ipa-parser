__all__ = [
    'IncompatibleTypesError',
]


class IncompatibleTypesError(ValueError):
    left: str
    right: str

    def __init__(self, left: str, right: str) -> None:
        super().__init__(f'{repr(left)} and {repr(right)} have incompatible types and cannot be concatenated')
        self.left = left
        self.right = right
