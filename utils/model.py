"""Model system with field-based validation and transformation.

Provides a lightweight alternative to Pydantic with a cleaner API for defining
validated data models with automatic transforms and validation.

Example:
    ```python
    from utils import Model, StringField, IntField, Field
    from utils import String, Integer

    class User(Model):
        email: StringField = StringField(
            transform=[String.strip, String.lower],
            validate=Validator.is_email
        )
        age: IntField = IntField(
            validate=(Integer.clamp, min=0, max=120)
        )
        name: StringField | None = None  # Optional field
        role: StringField = StringField(default="user")  # With default

    # Automatic transform + validation on init
    user = User(email="  ADMIN@EXAMPLE.COM  ", age=25)
    # user.email -> "admin@example.com"

    # Re-validates on assignment
    user.age = 30  # OK
    user.age = 150  # Raises ValidationError

    # Dict conversion
    data = user.to_dict()  # or user.model_dump()
    user2 = User.from_dict(data)  # or User.model_validate(data)

    # Custom objects with proper typing
    class Address:
        def __init__(self, street, city):
            self.street = street
            self.city = city

    class Person(Model):
        name: StringField = StringField()
        address: Field[Address] = Field[Address]()  # Required custom object
        metadata: dict | None = None  # Optional with type inference
    ```
"""

from __future__ import annotations

import inspect
import json
import types
from collections.abc import Callable
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Generic, Self, TypeVar, get_args, get_origin

T = TypeVar("T")


class ValidationError(Exception):
    """Raised when field validation fails."""

    pass


# ============================================================================
# Helper Functions for Callable Execution
# ============================================================================


def _function_accepts_param(func: Callable, param_name: str) -> bool:
    """Check if a function accepts a specific parameter."""
    sig = inspect.signature(func)
    return param_name in sig.parameters


def _call_with_context(
    func: Callable, value: Any, all_values: dict[str, Any], kwargs: dict
) -> Any:
    """Call function with optional all_values context parameter.

    Attempts to call with all_values first, falls back to without it.
    """
    if _function_accepts_param(func, "all_values"):
        return func(value, all_values=all_values, **kwargs)
    return func(value, **kwargs)


def _extract_callable_and_kwargs(
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


def _normalize_to_list(
    value: Callable | list[Callable | tuple] | None,
) -> list[Callable | tuple]:
    """Normalize a value to a list of callables/tuples."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


# ============================================================================
# Field Descriptor Classes
# ============================================================================


class Field(Generic[T]):
    """Base descriptor class for model fields with transform and validation.

    Handles transformation and validation of field values, supporting both
    callable transforms/validators and tuple syntax for passing arguments.

    Args:
        transform: Single transform function or list of transforms
        validate: Single validator function or validator with args as tuple
        default: Default value if not provided
        required: Whether field is required (default True)
    """

    def __init__(
        self,
        *,
        transform: Callable | list[Callable | tuple] | None = None,
        validate: Callable | tuple | list | None = None,
        default: Any = None,
        required: bool = True,
    ):
        self.transforms = _normalize_to_list(transform)
        self.validators = _normalize_to_list(validate)
        self.default = default
        self.required = required
        self.name: str | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        """Called when field is assigned to a class attribute."""
        self.name = name

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
            func, kwargs = _extract_callable_and_kwargs(transform)
            result = _call_with_context(func, result, all_values, kwargs)
        return result

    def _validate(self, value: Any, all_values: dict[str, Any]) -> None:
        """Run all validators on the value."""
        for validator in self.validators:
            func, kwargs = _extract_callable_and_kwargs(validator)
            result = _call_with_context(func, value, all_values, kwargs)

            if result is False:
                raise ValidationError(
                    f"Validation failed for field '{self.name}' with value: {value}"
                )


class StringField(Field[str]):
    """Field for string values with automatic type conversion."""

    def __set__(self, obj: Any, value: Any) -> None:
        """Convert value to string before processing."""
        if value is not None and not isinstance(value, str):
            value = str(value)
        super().__set__(obj, value)


class IntField(Field[int]):
    """Field for integer values with automatic type conversion."""

    def __set__(self, obj: Any, value: Any) -> None:
        """Convert value to int before processing."""
        if value is not None and not isinstance(value, int):
            value = self._convert_to_int(value)
        super().__set__(obj, value)

    def _convert_to_int(self, value: Any) -> int:
        """Convert value to int with error handling."""
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Field '{self.name}' cannot convert {value!r} to int: {e}"
            ) from e


class FloatField(Field[float]):
    """Field for float values with automatic type conversion."""

    def __set__(self, obj: Any, value: Any) -> None:
        """Convert value to float before processing."""
        if value is not None and not isinstance(value, float):
            value = self._convert_to_float(value)
        super().__set__(obj, value)

    def _convert_to_float(self, value: Any) -> float:
        """Convert value to float with error handling."""
        try:
            return float(value)
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Field '{self.name}' cannot convert {value!r} to float: {e}"
            ) from e


class BoolField(Field[bool]):
    """Field for boolean values with automatic type conversion."""

    def __set__(self, obj: Any, value: Any) -> None:
        """Convert value to bool before processing."""
        if value is not None and not isinstance(value, bool):
            value = self._convert_to_bool(value)
        super().__set__(obj, value)

    def _convert_to_bool(self, value: Any) -> bool:
        """Convert value to bool with string handling."""
        if isinstance(value, str):
            return self._parse_bool_string(value)
        return bool(value)

    def _parse_bool_string(self, value: str) -> bool:
        """Parse boolean from string representation."""
        value_lower = value.lower()
        if value_lower in ("true", "1", "yes", "on"):
            return True
        if value_lower in ("false", "0", "no", "off"):
            return False
        raise ValidationError(
            f"Field '{self.name}' cannot convert string {value!r} to bool"
        )


# ============================================================================
# Metaclass Helper Functions
# ============================================================================


def _is_optional_type(field_type: type) -> tuple[bool, type]:
    """Check if a type annotation is optional (Type | None).

    Returns:
        Tuple of (is_optional, actual_type)
    """
    origin = get_origin(field_type)
    if origin is types.UnionType:
        args = get_args(field_type)
        if type(None) in args:
            actual_type = next(arg for arg in args if arg is not type(None))
            return True, actual_type
    return False, field_type


def _create_field_for_type(field_type: type) -> Field:
    """Create appropriate Field instance for a given type annotation."""
    type_to_field = {
        StringField: StringField,
        IntField: IntField,
        FloatField: FloatField,
        BoolField: BoolField,
    }
    field_class = type_to_field.get(field_type, Field)
    return field_class(required=False)


def _process_field_annotation(
    field_name: str, field_type: type, namespace: dict
) -> tuple[Field, Any, bool] | None:
    """Process a single field annotation and return field metadata.

    Returns:
        Tuple of (field_instance, default, is_optional) or None if not a valid field
    """
    is_optional, actual_type = _is_optional_type(field_type)
    field_instance = namespace.get(field_name)

    # Case 1: Explicit Field instance provided
    if isinstance(field_instance, Field):
        return (field_instance, field_instance.default, is_optional)

    # Case 2: Optional field with None value (auto-create Field)
    if field_instance is None and is_optional:
        field = _create_field_for_type(actual_type)
        return (field, None, True)

    # Case 3: Not a valid field definition
    return None


def _apply_bulk_transforms(
    fields: dict[str, tuple[Field, Any, bool]], apply_transforms: dict
) -> None:
    """Apply bulk transforms to multiple fields."""
    for field_names, transforms in apply_transforms.items():
        transform_list = _normalize_to_list(transforms)
        for field_name in field_names:
            if field_name in fields:
                field_instance = fields[field_name][0]
                field_instance.transforms = transform_list + field_instance.transforms


def _apply_bulk_validators(
    fields: dict[str, tuple[Field, Any, bool]], apply_validators: dict
) -> None:
    """Apply bulk validators to multiple fields."""
    for field_names, validators in apply_validators.items():
        validator_list = _normalize_to_list(validators)
        for field_name in field_names:
            if field_name in fields:
                field_instance = fields[field_name][0]
                field_instance.validators = validator_list + field_instance.validators


# ============================================================================
# Model Metaclass
# ============================================================================


class ModelMeta(type):
    """Metaclass for Model that processes field definitions."""

    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> type:
        """Create new Model class and process field annotations."""
        cls = super().__new__(mcs, name, bases, namespace)

        # Don't process the base Model class itself
        if name == "Model":
            return cls

        # Process all field annotations
        fields = mcs._collect_fields(namespace)

        # Apply bulk transforms and validators
        apply_transforms = namespace.get("_apply_transforms", {})
        apply_validators = namespace.get("_apply_validators", {})
        _apply_bulk_transforms(fields, apply_transforms)
        _apply_bulk_validators(fields, apply_validators)

        # Store metadata on class
        cls._fields = fields
        cls._global_validators = namespace.get("_global_validators", [])

        # Set field descriptors as class attributes
        for field_name, (field_instance, _, _) in fields.items():
            setattr(cls, field_name, field_instance)

        return cls

    @staticmethod
    def _collect_fields(namespace: dict) -> dict[str, tuple[Field, Any, bool]]:
        """Collect and process all field annotations."""
        fields = {}
        annotations = namespace.get("__annotations__", {})

        for field_name, field_type in annotations.items():
            field_info = _process_field_annotation(field_name, field_type, namespace)
            if field_info:
                fields[field_name] = field_info

        return fields


# ============================================================================
# JSON Serialization Helpers
# ============================================================================


def _default_json_serializer(obj: Any) -> Any:
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


def _create_json_serializer(custom_serializer: Callable | None) -> Callable:
    """Create JSON serializer with optional custom serializer chaining."""
    if not custom_serializer:
        return _default_json_serializer

    def chained_serializer(obj: Any) -> Any:
        try:
            return custom_serializer(obj)
        except TypeError:
            return _default_json_serializer(obj)

    return chained_serializer


# ============================================================================
# Model Base Class
# ============================================================================


class Model(metaclass=ModelMeta):
    """Base class for validated data models.

    Provides automatic field validation, transformation, and dict conversion.
    Subclasses define fields using Field descriptors with type annotations.

    Example:
        ```python
        class User(Model):
            email: StringField = StringField(transform=[str.lower])
            age: IntField = IntField(validate=(lambda x: x >= 0))
            name: StringField | None = None
        ```
    """

    _fields: dict[str, tuple[Field, Any, bool]]
    _global_validators: list[Callable]

    def __init__(self, **kwargs: Any):
        """Initialize model with field values.

        Args:
            **kwargs: Field values to set

        Raises:
            ValidationError: If required fields are missing or validation fails
        """
        self._initialize_fields(kwargs)
        self._run_global_validators()

    def _initialize_fields(self, kwargs: dict[str, Any]) -> None:
        """Initialize all fields with provided or default values."""
        for field_name, (field, default, is_optional) in self._fields.items():
            if field_name in kwargs:
                setattr(self, field_name, kwargs[field_name])
            elif default is not None:
                setattr(self, field_name, default)
            elif is_optional:
                setattr(self, field_name, None)
            elif field.required:
                raise ValidationError(f"Required field '{field_name}' is missing")

    def _run_global_validators(self) -> None:
        """Run global validators with all field values."""
        if not hasattr(self, "_global_validators"):
            return

        values = self.to_dict()
        for validator in self._global_validators:
            self._execute_global_validator(validator, values)

    def _execute_global_validator(
        self, validator: Callable, values: dict[str, Any]
    ) -> None:
        """Execute a single global validator with error handling."""
        try:
            result = validator(values)
            if result is False:
                raise ValidationError(
                    f"Global validation failed for {self.__class__.__name__}"
                )
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(
                f"Global validation error in {self.__class__.__name__}: {e}"
            ) from e

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary.

        Returns:
            Dictionary with all field values
        """
        return {
            field_name: getattr(self, field_name)
            for field_name in self._fields
            if hasattr(self, field_name)
        }

    def model_dump(self) -> dict[str, Any]:
        """Pydantic-compatible alias for to_dict."""
        return self.to_dict()

    def json(self, **kwargs: Any) -> str:
        """Serialize model to JSON string.

        Args:
            **kwargs: Arguments to pass to json.dumps (indent, default, etc.)
                     Can include a custom 'default' serializer which will be
                     chained with the built-in serializer.

        Returns:
            JSON string representation of the model
        """
        custom_serializer = kwargs.pop("default", None)
        serializer = _create_json_serializer(custom_serializer)
        return json.dumps(self.to_dict(), default=serializer, **kwargs)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create model instance from dictionary.

        Args:
            data: Dictionary with field values

        Returns:
            New model instance

        Raises:
            ValidationError: If validation fails
        """
        return cls(**data)

    @classmethod
    def model_validate(cls, data: dict[str, Any]) -> Self:
        """Pydantic-compatible alias for from_dict."""
        return cls.from_dict(data)

    @classmethod
    def model_validate_json(cls, json_data: str) -> Self:
        """Create model instance from JSON string.

        Args:
            json_data: JSON string to parse

        Returns:
            New model instance

        Raises:
            ValidationError: If validation fails
        """
        try:
            data = json.loads(json_data)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON: {e}") from e

    def __repr__(self) -> str:
        """Return string representation of model."""
        field_strs = [f"{k}={v!r}" for k, v in self.to_dict().items()]
        return f"{self.__class__.__name__}({', '.join(field_strs)})"

    def __eq__(self, other: Any) -> bool:
        """Compare models for equality."""
        if not isinstance(other, self.__class__):
            return False
        return self.to_dict() == other.to_dict()


__all__ = [
    "Model",
    "Field",
    "StringField",
    "IntField",
    "FloatField",
    "BoolField",
    "ValidationError",
]
