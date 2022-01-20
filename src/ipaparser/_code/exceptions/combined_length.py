__all__ = [
    'CombinedLengthError',
]


class CombinedLengthError(ValueError):
    sequence: tuple[str, ...]

    def __init__(self, sequence: tuple[str, ...]) -> None:
        super().__init__(f'A sound sequence to be combined must contain at least 2 elements'
                         f' (got {len(sequence)}{f": {repr(sequence[0])}" if sequence else ""})')
        self.sequence = sequence
