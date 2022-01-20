__all__ = [
    'CombinedSoundError',
]


class CombinedSoundError(ValueError):
    sound: str

    def __init__(self, sound: str) -> None:
        super().__init__(f'A sound to be combined must start with a non-combining character (got {repr(" " + sound)})'
                         if sound else 'A sound to be combined cannot be empty')
        self.sound = sound
