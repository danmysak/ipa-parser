from typing import Any, Callable, TypeVar

__all__ = [
    'load',
    'with_cache',
]

T = TypeVar('T')

CACHE: dict[Callable, Any] = {}
RETRIEVERS: dict[Callable, Callable] = {}


def with_cache(loader: Callable[[], T]) -> Callable[[], T]:
    def retrieve() -> T:
        if loader not in CACHE:
            CACHE[loader] = loader()
        return CACHE[loader]

    RETRIEVERS[loader] = retrieve
    return retrieve


def load() -> None:
    """Eagerly load and preprocess supporting data so that the first parse is a bit faster."""
    for retrieve in RETRIEVERS.values():
        retrieve()
