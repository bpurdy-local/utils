"""Computed field decorator and descriptor for Model system."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class ComputedFieldDescriptor:
    """Descriptor for computed fields that are included in serialization."""

    def __init__(self, func: Callable, alias: str | None = None):
        self.func = func
        self.alias = alias
        self.name: str | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        """Called when descriptor is assigned to a class attribute."""
        self.name = name

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        """Compute and return the field value."""
        if obj is None:
            return self
        return self.func(obj)

    def get_serialization_key(self, alias_generator: Callable[[str], str] | None = None) -> str:
        """Get the key to use for serialization (alias or field name)."""
        # Explicit alias takes precedence
        if self.alias:
            return self.alias

        # Try alias generator if provided
        if alias_generator and self.name:
            return alias_generator(self.name)

        # Fall back to field name
        return self.name or ""


def computed_field(func: Callable | None = None, *, alias: str | None = None) -> Any:
    """Decorator to mark a method as a computed field that appears in serialization.

    Computed fields are read-only properties whose values are calculated from other
    fields and included in to_dict() and json() output.

    Args:
        func: The method to wrap (when used without arguments)
        alias: Optional alias for serialization

    Example:
        ```python
        class User(Model):
            first_name: StringField = StringField()
            last_name: StringField = StringField()

            @computed_field
            def full_name(self) -> str:
                return f"{self.first_name} {self.last_name}"

            @computed_field(alias="displayName")
            def display_name(self) -> str:
                return self.full_name.upper()
        ```
    """

    def decorator(f: Callable) -> ComputedFieldDescriptor:
        return ComputedFieldDescriptor(f, alias=alias)

    if func is None:
        # Called with arguments: @computed_field(alias="...")
        return decorator
    else:
        # Called without arguments: @computed_field
        return decorator(func)
