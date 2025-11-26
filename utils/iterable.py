from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")
K = TypeVar("K")


class Iterable:
    """Static utility class for iterable operations."""

    @staticmethod
    def chunk(items: list[T], *, size: int) -> list[list[T]]:
        """Split iterable into chunks of specified size.

        Examples:
            >>> Iterable.chunk([1, 2, 3, 4, 5], size=2)
            [[1, 2], [3, 4], [5]]
        """
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
        """Flatten nested lists and tuples into a single list.

        Examples:
            >>> Iterable.flatten([1, [2, 3], 4, [5, 6]])
            [1, 2, 3, 4, 5, 6]
        """
        result = []
        for item in items:
            if isinstance(item, list | tuple):
                result.extend(item)
            else:
                result.append(item)
        return result

    @staticmethod
    def unique(items: list[T], *, key: Callable[[T], Any] | None = None) -> list[T]:
        """Get unique items from list, preserving order.

        Examples:
            >>> Iterable.unique([1, 2, 2, 3, 1, 4])
            [1, 2, 3, 4]
        """
        seen = set()
        result = []
        for item in items:
            k = key(item) if key else item  # Use key function to determine uniqueness
            if k not in seen:
                seen.add(k)
                result.append(item)
        return result

    @staticmethod
    def first(items: list[T], *, default: T | None = None) -> T | None:
        """Get first item from list, or default if empty."""
        if len(items) == 0:
            return default
        return items[0]

    @staticmethod
    def last(items: list[T], *, default: T | None = None) -> T | None:
        """Get last item from list, or default if empty."""
        if len(items) == 0:
            return default
        return items[-1]

    @staticmethod
    def find_first(items: list[T], *, predicate: Callable[[T], bool]) -> T | None:
        """Return first item matching predicate or None if no match.

        Args:
            items: The list to search
            predicate: Function to test each item (keyword-only)

        Returns:
            First matching item or None

        Examples:
            >>> numbers = [1, 2, 3, 4, 5]
            >>> Iterable.find_first(numbers, predicate=lambda x: x > 3)
            4

            >>> Iterable.find_first(numbers, predicate=lambda x: x > 10)

            >>> users = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
            >>> Iterable.find_first(users, predicate=lambda u: u["age"] > 28)
            {'name': 'Alice', 'age': 30}
        """
        for item in items:
            if predicate(item):
                return item
        return None

    @staticmethod
    def find_last(items: list[T], *, predicate: Callable[[T], bool]) -> T | None:
        """Return last item matching predicate or None if no match.

        Args:
            items: The list to search
            predicate: Function to test each item (keyword-only)

        Returns:
            Last matching item or None

        Examples:
            >>> numbers = [1, 2, 3, 4, 5, 4, 3]
            >>> Iterable.find_last(numbers, predicate=lambda x: x == 4)
            4

            >>> Iterable.find_last(numbers, predicate=lambda x: x > 10)
        """
        last_match = None
        for item in items:
            if predicate(item):
                last_match = item
        return last_match

    @staticmethod
    def find_all(items: list[T], *, predicate: Callable[[T], bool]) -> list[T]:
        """Return all items matching predicate.

        Args:
            items: The list to search
            predicate: Function to test each item (keyword-only)

        Returns:
            List of all matching items (empty list if no matches)

        Examples:
            >>> numbers = [1, 2, 3, 4, 5]
            >>> Iterable.find_all(numbers, predicate=lambda x: x > 3)
            [4, 5]

            >>> Iterable.find_all(numbers, predicate=lambda x: x > 10)
            []
        """
        return [item for item in items if predicate(item)]

    @staticmethod
    def group_by(items: list[T], *, key: Callable[[T], K]) -> dict[K, list[T]]:
        """Group items by key function.

        Examples:
            >>> Iterable.group_by([1, 2, 3, 4, 5], key=lambda x: x % 2)
            {1: [1, 3, 5], 0: [2, 4]}
        """
        result: dict[K, list[T]] = {}
        for item in items:
            k = key(item)
            if k not in result:
                result[k] = []
            result[k].append(item)
        return result

    @staticmethod
    def partition(items: list[T], *, predicate: Callable[[T], bool]) -> tuple[list[T], list[T]]:
        """Partition items into two lists based on predicate.

        Examples:
            >>> Iterable.partition([1, 2, 3, 4, 5], predicate=lambda x: x % 2 == 0)
            ([2, 4], [1, 3, 5])
        """
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
        """Extract values from list of dicts by key.

        Examples:
            >>> items = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
            >>> Iterable.pluck(items, key='name')
            ['Alice', 'Bob']
        """
        result = []
        for item in items:
            if isinstance(item, dict) and key in item:
                result.append(item[key])
        return result

    @staticmethod
    def filter_map(items: list[T], *, func: Callable[[T], Any | None]) -> list[Any]:
        """Map function over items and filter out None results."""
        result = []
        for item in items:
            mapped = func(item)
            if mapped is not None:
                result.append(mapped)
        return result

    @staticmethod
    def compact(items: list[T]) -> list[T]:
        """Remove None values from list."""
        return [item for item in items if item is not None]

    @staticmethod
    def count_by(items: list[T], *, key: Callable[[T], K] | None = None) -> dict[K, int]:
        """Count occurrences of items, optionally grouped by key function.

        Examples:
            >>> Iterable.count_by(['a', 'b', 'a', 'c', 'b', 'a'])
            {'a': 3, 'b': 2, 'c': 1}
        """
        result: dict[K, int] = {}
        for item in items:
            k = key(item) if key else item  # type: ignore
            result[k] = result.get(k, 0) + 1  # type: ignore
        return result

    @staticmethod
    def take(items: list[T], *, n: int) -> list[T]:
        """Take first n items from list."""
        return items[:n]

    @staticmethod
    def drop(items: list[T], *, n: int) -> list[T]:
        """Drop first n items from list."""
        return items[n:]

    @staticmethod
    def sum_by(items: list[T], *, key: Callable[[T], int | float] | None = None) -> int | float:
        """Sum items, optionally using key function."""
        if key:
            return sum(key(item) for item in items)
        return sum(item for item in items if isinstance(item, int | float))

    @staticmethod
    def average(items: list[T]) -> float:
        """Calculate average of numeric items."""
        numeric_items = [item for item in items if isinstance(item, int | float)]
        if not numeric_items:
            raise ValueError("Cannot calculate average of non-numeric items")
        return sum(numeric_items) / len(numeric_items)
