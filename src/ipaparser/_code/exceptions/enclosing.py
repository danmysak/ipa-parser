__all__ = [
    'EnclosingError',
]


class EnclosingError(ValueError):
    transcription: str

    def __init__(self, transcription: str) -> None:
        super().__init__(f'"{transcription}" is not properly enclosed in brackets (like [so] or /so/)')
        self.transcription = transcription
