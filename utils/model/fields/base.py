"""Base Field class for Model system."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Generic, Self, TypeVar

from utils.model.helpers import call_with_context, extract_callable_and_kwargs, normalize_to_list

T = TypeVar("T")


class Field(Generic[T]):
    """Base descriptor class for model fields with transform and validation.

    Handles transformation and validation of field values, supporting both
    callable transforms/validators and tuple syntax for passing arguments.

    Args:
        transform: Single transform function or list of transforms
        validate: Single validator function or validator with args as tuple
        default: Default value if not provided
        required: Whether field is required (default True)
        alias: Alternative name for serialization (to_dict/json)
        exclude: Exclude from all serialization
        exclude_from_dict: Exclude only from to_dict()
        exclude_from_json: Exclude only from json()
    """

    def __init__(
        self,
        *,
        transform: Callable | list[Callable | tuple] | None = None,
        validate: Callable | tuple | list | None = None,
        default: Any = None,
        required: bool = True,
        alias: str | None = None,
        exclude: bool = False,
        exclude_from_dict: bool = False,
        exclude_from_json: bool = False,
    ):
        self.transforms = normalize_to_list(transform)
        self.validators = normalize_to_list(validate)
        self.default = default
        self.required = required
        self.alias = alias
        self.exclude = exclude
        self.exclude_from_dict = exclude_from_dict
        self.exclude_from_json = exclude_from_json
        self.name: str | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        """Called when field is assigned to a class attribute."""
        self.name = name

    def get_serialization_key(self, alias_generator: Callable[[str], str] | None = None) -> str:
        """Get the key to use for serialization (alias or field name).

        Args:
            alias_generator: Optional function to generate alias from field name

        Returns:
            Serialization key (explicit alias, generated alias, or field name)
        """
        # Explicit alias takes precedence
        if self.alias:
            return self.alias

        # Try alias generator if provided
        if alias_generator and self.name:
            return alias_generator(self.name)

        # Fall back to field name
        return self.name or ""

    def __get__(self, obj: Any, objtype: type | None = None) -> T | Self:
        """Get the field value from the instance."""
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj: Any, value: Any) -> None:
        """Set and validate the field value on the instance."""
        if self._should_skip_processing(value):
            obj.__dict__[self.name] = None
            return

        all_values = obj.__dict__.copy()
        processed_value = self._apply_transforms(value, all_values)
        self._validate(processed_value, all_values)
        obj.__dict__[self.name] = processed_value

    def _should_skip_processing(self, value: Any) -> bool:
        """Check if we should skip transforms/validation for this value."""
        return value is None and not self.required

    def _apply_transforms(self, value: Any, all_values: dict[str, Any]) -> Any:
        """Apply all transforms in sequence."""
        result = value
        for transform in self.transforms:
            func, kwargs = extract_callable_and_kwargs(transform)
            result = call_with_context(func, result, all_values, kwargs)
        return result

    def _validate(self, value: Any, all_values: dict[str, Any]) -> None:
        """Run all validators on the value."""
        from utils.model.exceptions import ValidationError

        for validator in self.validators:
            func, kwargs = extract_callable_and_kwargs(validator)
            result = call_with_context(func, value, all_values, kwargs)

            if result is False:
                raise ValidationError(
                    f"Validation failed for field '{self.name}' with value: {value}"
                )
