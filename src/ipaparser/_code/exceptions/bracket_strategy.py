__all__ = [
    'BracketStrategyError',
]


class BracketStrategyError(ValueError):
    value: str

    def __init__(self, value: str, valid: list[str]) -> None:
        super().__init__(f'{repr(value)} is not a valid strategy;'
                         f' use one of the following: {"/".join(map(repr, valid))}')
        self.value = value
