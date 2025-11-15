"""Miscellaneous utility functions (backward compatibility wrappers)."""

from utils.decorators import Decorators
from utils.integer import Integer
from utils.random_utils import Random
from utils.string import String


def generate_id(length: int = 8, chars: str | None = None) -> str:
    """Generate random ID string (backward compatibility wrapper).

    Args:
        length: Length of ID
        chars: Characters to use (defaults to alphanumeric)

    Returns:
        Random ID string
    """
    return Random.string(length=length, chars=chars)


def hash_string(text: str, algorithm: str = "sha256") -> str:
    """Hash a string (backward compatibility wrapper).

    Args:
        text: String to hash
        algorithm: Hash algorithm (md5, sha1, sha256, sha512)

    Returns:
        Hexadecimal hash string
    """
    return String.hash(text, algorithm=algorithm)


def clamp(value: int, min_val: int, max_val: int) -> int:
    """Clamp value between min and max (backward compatibility wrapper).

    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        Clamped value
    """
    return Integer.clamp(value, min_val=min_val, max_val=max_val)


def memoize(func):
    """Memoize function (backward compatibility wrapper).

    Args:
        func: Function to memoize

    Returns:
        Memoized function
    """
    return Decorators.memoize(func)


def once(func):
    """Ensure function is only called once (backward compatibility wrapper).

    Args:
        func: Function to call once

    Returns:
        Wrapped function that only executes once
    """
    return Decorators.once(func)


def bytes_to_human(size: int) -> str:
    """Convert bytes to human-readable format (backward compatibility wrapper).

    Args:
        size: Size in bytes

    Returns:
        Human-readable size string
    """
    return Integer.bytes_to_human(size)


def percentage(value: float, total: float, decimals: int = 1) -> float:
    """Calculate percentage (backward compatibility wrapper).

    Args:
        value: Value to calculate percentage of
        total: Total value
        decimals: Number of decimal places

    Returns:
        Percentage value
    """
    return Integer.percentage(int(value), total=int(total), decimals=decimals)
