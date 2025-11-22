"""JSON serialization helpers for Model system."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any


def to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase.

    Args:
        snake_str: String in snake_case format

    Returns:
        String in camelCase format
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def default_json_serializer(obj: Any) -> Any:
    """Default JSON serializer for common Python types."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, Path):
        return str(obj)
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def create_json_serializer(custom_serializer: Callable | None) -> Callable:
    """Create JSON serializer with optional custom serializer chaining."""
    if not custom_serializer:
        return default_json_serializer

    def chained_serializer(obj: Any) -> Any:
        try:
            return custom_serializer(obj)
        except TypeError:
            return default_json_serializer(obj)

    return chained_serializer
