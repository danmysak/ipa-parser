__all__ = [
    'CombinedLengthError'
]


class CombinedLengthError(ValueError):
    sequence: tuple[str, ...]

    def __init__(self, sequence: tuple[str, ...]):
        super().__init__(f'A sound sequence to be combined must contain at least two elements'
                         f' (got {len(sequence)}{f": {sequence[0]}" if sequence else ""})')
        self.sequence = sequence
