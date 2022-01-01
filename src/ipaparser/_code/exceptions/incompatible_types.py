__all__ = [
    'IncompatibleTypesError',
]


class IncompatibleTypesError(ValueError):
    def __init__(self, left_transcription: str, right_transcription: str) -> None:
        super().__init__(f'{left_transcription} and {right_transcription} have incompatible types')
