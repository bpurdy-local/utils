from collections.abc import Callable, Iterable
from typing import Any, TypeVar

from utils.dict import Dict
from utils.iterable import Iterable as IterableClass

T = TypeVar("T")
K = TypeVar("K")


class Collection:
    @staticmethod
    def unique(iterable: Iterable[T], key: Callable[[T], Any] | None = None) -> list[T]:
        return IterableClass.unique(list(iterable), key=key)

    @staticmethod
    def first(iterable: Iterable[T], default: T | None = None) -> T | None:
        return IterableClass.first(list(iterable), default=default)

    @staticmethod
    def last(iterable: Iterable[T], default: T | None = None) -> T | None:
        return IterableClass.last(list(iterable), default=default)

    @staticmethod
    def pluck(iterable: Iterable[dict[str, Any]], key: str) -> list[Any]:
        return IterableClass.pluck(list(iterable), key=key)

    @staticmethod
    def omit(d: dict[str, Any], *keys: str) -> dict[str, Any]:
        return Dict.omit(d, *keys)

    @staticmethod
    def pick(d: dict[str, Any], *keys: str) -> dict[str, Any]:
        return Dict.pick(d, *keys)

    @staticmethod
    def partition(iterable: Iterable[T], predicate: Callable[[T], bool]) -> tuple[list[T], list[T]]:
        return IterableClass.partition(list(iterable), predicate=predicate)

    @staticmethod
    def zip_dict(keys: Iterable[K], values: Iterable[T]) -> dict[K, T]:
        return dict(zip(keys, values, strict=False))
