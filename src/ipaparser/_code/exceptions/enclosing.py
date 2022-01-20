__all__ = [
    'EnclosingError',
]


class EnclosingError(ValueError):
    transcription: str

    def __init__(self, transcription: str) -> None:
        super().__init__(f'{repr(transcription)} is not properly delimited (like [so] or /so/)')
        self.transcription = transcription
