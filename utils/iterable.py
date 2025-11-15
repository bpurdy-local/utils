from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")
K = TypeVar("K")


class Iterable:
    @staticmethod
    def chunk(items: list[T], *, size: int) -> list[list[T]]:
        result = []
        current_chunk = []
        for item in items:
            current_chunk.append(item)
            if len(current_chunk) == size:
                result.append(current_chunk)
                current_chunk = []
        if current_chunk:
            result.append(current_chunk)
        return result

    @staticmethod
    def flatten(items: list[T]) -> list[T]:
        result = []
        for item in items:
            if isinstance(item, (list, tuple)):
                result.extend(item)
            else:
                result.append(item)
        return result

    @staticmethod
    def unique(items: list[T], *, key: Callable[[T], Any] | None = None) -> list[T]:
        seen = set()
        result = []
        for item in items:
            k = key(item) if key else item
            if k not in seen:
                seen.add(k)
                result.append(item)
        return result

    @staticmethod
    def first(items: list[T], *, default: T | None = None) -> T | None:
        if len(items) == 0:
            return default
        return items[0]

    @staticmethod
    def last(items: list[T], *, default: T | None = None) -> T | None:
        if len(items) == 0:
            return default
        return items[-1]

    @staticmethod
    def group_by(items: list[T], *, key: Callable[[T], K]) -> dict[K, list[T]]:
        result: dict[K, list[T]] = {}
        for item in items:
            k = key(item)
            if k not in result:
                result[k] = []
            result[k].append(item)
        return result

    @staticmethod
    def partition(items: list[T], *, predicate: Callable[[T], bool]) -> tuple[list[T], list[T]]:
        true_list = []
        false_list = []
        for item in items:
            if predicate(item):
                true_list.append(item)
            else:
                false_list.append(item)
        return (true_list, false_list)

    @staticmethod
    def pluck(items: list[T], *, key: str) -> list[Any]:
        result = []
        for item in items:
            if isinstance(item, dict) and key in item:
                result.append(item[key])
        return result

    @staticmethod
    def filter_map(items: list[T], *, func: Callable[[T], Any | None]) -> list[Any]:
        result = []
        for item in items:
            mapped = func(item)
            if mapped is not None:
                result.append(mapped)
        return result

    @staticmethod
    def compact(items: list[T]) -> list[T]:
        return [item for item in items if item is not None]

    @staticmethod
    def count_by(items: list[T], *, key: Callable[[T], K] | None = None) -> dict[K, int]:
        result: dict[K, int] = {}
        for item in items:
            k = key(item) if key else item  # type: ignore
            result[k] = result.get(k, 0) + 1  # type: ignore
        return result

    @staticmethod
    def sort_by(
        items: list[T], *, key: Callable[[T], Any] | None = None, reverse: bool = False
    ) -> list[T]:
        return sorted(items, key=key, reverse=reverse)  # type: ignore

    @staticmethod
    def take(items: list[T], *, n: int) -> list[T]:
        return items[:n]

    @staticmethod
    def drop(items: list[T], *, n: int) -> list[T]:
        return items[n:]

    @staticmethod
    def sum_by(items: list[T], *, key: Callable[[T], int | float] | None = None) -> int | float:
        if key:
            return sum(key(item) for item in items)
        return sum(item for item in items if isinstance(item, (int, float)))

    @staticmethod
    def average(items: list[T]) -> float:
        numeric_items = [item for item in items if isinstance(item, (int, float))]
        if not numeric_items:
            raise ValueError("Cannot calculate average of non-numeric items")
        return sum(numeric_items) / len(numeric_items)
