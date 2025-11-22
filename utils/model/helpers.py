"""Helper functions for Model system."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any


def function_accepts_param(func: Callable, param_name: str) -> bool:
    """Check if a function accepts a specific parameter."""
    sig = inspect.signature(func)
    return param_name in sig.parameters


def call_with_context(func: Callable, value: Any, all_values: dict[str, Any], kwargs: dict) -> Any:
    """Call function with optional all_values context parameter or auto-injected fields.

    Supports three calling modes:
    1. With all_values parameter: func(value, all_values=dict, **kwargs)
    2. With auto-injected field values: func(value, field1=val1, field2=val2, **kwargs)
    3. Without context: func(value, **kwargs)
    """
    sig = inspect.signature(func)

    # Check if function accepts all_values parameter
    if "all_values" in sig.parameters:
        return func(value, all_values=all_values, **kwargs)

    # Check for auto-injectable field parameters
    auto_inject = {}
    for param_name in sig.parameters:
        # Skip special parameters
        if param_name in ("self", "cls", "args", "kwargs"):
            continue
        # Only inject if parameter name matches a field and not already in kwargs
        if param_name in all_values and param_name not in kwargs:
            auto_inject[param_name] = all_values[param_name]

    # Merge auto-injected values with existing kwargs
    combined_kwargs = {**auto_inject, **kwargs}
    return func(value, **combined_kwargs)


def extract_callable_and_kwargs(
    item: Callable | tuple,
) -> tuple[Callable, dict[str, Any]]:
    """Extract callable and kwargs from a transform/validator item.

    Supports both:
    - Simple callable: func
    - Tuple with kwargs: (func, {'key': 'val'})
    """
    if isinstance(item, tuple):
        func = item[0]
        kwargs = {}
        # Extract all dict items from tuple
        for element in item[1:]:
            if isinstance(element, dict):
                kwargs.update(element)
        return func, kwargs
    return item, {}


def normalize_to_list(
    value: Callable | list[Callable | tuple] | None,
) -> list[Callable | tuple]:
    """Normalize a value to a list of callables/tuples."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]
