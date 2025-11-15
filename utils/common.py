"""Common utility functions (thin wrappers for backward compatibility)."""

from collections.abc import Callable, Iterable
from typing import Any, TypeVar

from utils.decorators import Decorators
from utils.iterable import Iterable as IterableClass
from utils.string import String

T = TypeVar("T")
K = TypeVar("K")


def chunk(iterable: Iterable[T], size: int) -> list[list[T]]:
    """Split iterable into chunks of specified size.

    Args:
        iterable: Iterable to chunk
        size: Size of each chunk

    Returns:
        List of chunks

    Examples:
        >>> chunk([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
    """
    return [list(chunk) for chunk in IterableClass.chunk(list(iterable), size=size)]


def flatten(nested_list: Iterable[Iterable[T]]) -> list[T]:
    """Flatten a nested list one level.

    Args:
        nested_list: Nested iterable to flatten

    Returns:
        Flattened list

    Examples:
        >>> flatten([[1, 2], [3, 4]])
        [1, 2, 3, 4]
    """
    return list(IterableClass.flatten(list(nested_list)))  # type: ignore


def group_by(iterable: Iterable[T], key: Callable[[T], K]) -> dict[K, list[T]]:
    """Group items in iterable by key function.

    Args:
        iterable: Iterable to group
        key: Function to extract key from each item

    Returns:
        Dictionary mapping keys to lists of items

    Examples:
        >>> group_by([1, 2, 3, 4], lambda x: x % 2)
        {0: [2, 4], 1: [1, 3]}
    """
    result = IterableClass.group_by(list(iterable), key=key)
    return {k: list(v) for k, v in result.items()}


def debounce(delay: float) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Debounce a function call (backward compatibility wrapper).

    Args:
        delay: Delay in seconds

    Returns:
        Decorator function
    """
    return Decorators.debounce(delay=delay)


def throttle(delay: float) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Throttle a function call (backward compatibility wrapper).

    Args:
        delay: Minimum delay between calls in seconds

    Returns:
        Decorator function
    """
    return Decorators.throttle(delay=delay)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Retry decorator (backward compatibility wrapper).

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch and retry on

    Returns:
        Decorator function
    """
    return Decorators.retry(
        max_attempts=max_attempts, delay=delay, backoff=backoff, exceptions=exceptions
    )


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug (backward compatibility wrapper).

    Args:
        text: Text to slugify

    Returns:
        Slugified string

    Examples:
        >>> slugify("Hello World!")
        'hello-world'
    """
    return str(String.slug(text))
