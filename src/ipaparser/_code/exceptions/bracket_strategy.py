__all__ = [
    'BracketStrategyError',
]


class BracketStrategyError(ValueError):
    value: str

    def __init__(self, value: str, valid: list[str]):
        super().__init__(f'"{value}" is not a valid strategy; use one of the following: {"/".join(valid)}')
        self.value = value
