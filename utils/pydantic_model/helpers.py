"""Helper functions for Pydantic Model system."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any


def normalize_to_list(value: Any) -> list:
    """Normalize value to list.

    Args:
        value: Single item or list

    Returns:
        List containing the item(s)
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def call_with_context(
    func: Callable,
    value: Any,
    kwargs: dict[str, Any],
    all_values: dict[str, Any],
) -> Any:
    """Call function with context-aware parameter injection.

    Supports three calling modes:
    1. all_values parameter - passes entire dict
    2. Auto-injection - injects field values by parameter name
    3. Regular - just passes explicit kwargs

    Args:
        func: Function to call
        value: Primary value to pass
        kwargs: Explicit keyword arguments
        all_values: All field values for context

    Returns:
        Function result
    """
    sig = inspect.signature(func)
    params = sig.parameters

    # Check if function accepts all_values parameter
    if "all_values" in params:
        return func(value, all_values=all_values, **kwargs)

    # Auto-inject field values if not in kwargs
    injected_kwargs = kwargs.copy()

    # Get the first parameter name (which receives the value)
    param_names = list(params.keys())
    first_param = param_names[0] if param_names else None

    for param_name, param in params.items():
        # Skip first positional param (receives the value argument)
        if param_name == first_param:
            continue

        # Skip self/cls
        if param_name in ("self", "cls"):
            continue

        # Skip if already provided
        if param_name in kwargs:
            continue

        # Skip if no default and not in all_values
        if param.default is inspect.Parameter.empty and param_name not in all_values:
            continue

        # Inject from all_values if available
        if param_name in all_values:
            injected_kwargs[param_name] = all_values[param_name]

    return func(value, **injected_kwargs)
