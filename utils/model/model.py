"""Base Model class for validated data models."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any, Self

from utils.model.exceptions import ValidationError
from utils.model.fields import Field
from utils.model.metaclass import ModelMeta
from utils.model.serialization import create_json_serializer


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

    Config:
        ```python
        class User(Model):
            class Config:
                # Auto-generate aliases for all fields
                alias_generator = to_camel

                # Apply transforms to multiple fields
                apply_transforms = {
                    ("email", "username"): [str.strip, str.lower]
                }

                # Apply validators to multiple fields
                apply_validators = {
                    ("email", "username"): lambda x: len(x) > 0
                }

                # Global validators with cross-field logic
                global_validators = [
                    lambda vals: vals["age"] >= 18 or vals["role"] != "admin"
                ]

                # Handle unknown fields: "store" (default), "strict", or "ignore"
                # "store": Store unknown fields in _extra_fields dict
                # "strict": Raise ValidationError on unknown fields
                # "ignore": Silently ignore unknown fields
                extra_fields_mode = "store"

                # Custom JSON serializer for all json() calls (can be overridden per-call)
                json_serializer = custom_serializer_function

            user_name: StringField = StringField()  # Serializes as "userName"
            email: StringField = StringField()
            username: StringField = StringField()
            age: IntField = IntField()
            role: StringField = StringField()
        ```
    """

    _fields: dict[str, tuple[Field, Any, bool]]
    _global_validators: list[Callable]
    _alias_generator: Callable[[str], str] | None
    _extra_fields_mode: str  # "store", "strict", or "ignore"
    _extra_fields: dict[str, Any]

    def __init__(self, **kwargs: Any):
        """Initialize model with field values.

        Args:
            **kwargs: Field values to set

        Raises:
            ValidationError: If required fields are missing or validation fails
        """
        self._extra_fields = {}
        self._initialize_fields(kwargs)
        self._run_global_validators()

    def _initialize_fields(self, kwargs: dict[str, Any]) -> None:
        """Initialize all fields with provided or default values."""
        # First, initialize known fields
        for field_name, (field, default, is_optional) in self._fields.items():
            if field_name in kwargs:
                setattr(self, field_name, kwargs[field_name])
            elif default is not None:
                setattr(self, field_name, default)
            elif is_optional:
                setattr(self, field_name, None)
            elif field.required:
                raise ValidationError(f"Required field '{field_name}' is missing")

        # Handle unknown fields based on extra_fields_mode
        extra_fields_mode = getattr(self.__class__, "_extra_fields_mode", "store")
        unknown_fields = set(kwargs.keys()) - set(self._fields.keys())

        if unknown_fields:
            if extra_fields_mode == "strict":
                # Raise error on unknown fields
                fields_list = ", ".join(f"'{f}'" for f in sorted(unknown_fields))
                raise ValidationError(f"Unknown field(s) provided: {fields_list}")
            elif extra_fields_mode == "store":
                # Store unknown fields in _extra_fields dict
                for field_name in unknown_fields:
                    self._extra_fields[field_name] = kwargs[field_name]
            # else: mode is "ignore", do nothing

    def _run_global_validators(self) -> None:
        """Run global validators with all field values."""
        if not hasattr(self, "_global_validators"):
            return

        values = self.to_dict()
        for validator in self._global_validators:
            self._execute_global_validator(validator, values)

    def _execute_global_validator(self, validator: Callable, values: dict[str, Any]) -> None:
        """Execute a single global validator with error handling."""
        try:
            result = validator(values)
            if result is False:
                raise ValidationError(f"Global validation failed for {self.__class__.__name__}")
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(
                f"Global validation error in {self.__class__.__name__}: {e}"
            ) from e

    def to_dict(
        self, exclude_none: bool = False, exclude_fields: list[str] | None = None
    ) -> dict[str, Any]:
        """Convert model to dictionary.

        Args:
            exclude_none: If True, exclude fields with None values
            exclude_fields: List of field names to exclude from output

        Returns:
            Dictionary with all field values (including computed fields)
        """
        exclude_fields = exclude_fields or []
        result = {}
        alias_generator = getattr(self.__class__, "_alias_generator", None)

        # Add regular fields
        for field_name, (field, _, _) in self._fields.items():
            # Skip if field is in exclude list
            if field_name in exclude_fields:
                continue

            # Skip if field is excluded from dict
            if field.exclude or field.exclude_from_dict:
                continue

            if not hasattr(self, field_name):
                continue

            value = getattr(self, field_name)

            # Skip None values if requested
            if exclude_none and value is None:
                continue

            # Use alias (explicit or generated)
            key = field.get_serialization_key(alias_generator)
            result[key] = value

        # Add computed fields
        computed_fields = getattr(self.__class__, "_computed_fields", {})
        for field_name, computed_field in computed_fields.items():
            # Skip if field is in exclude list
            if field_name in exclude_fields:
                continue

            value = getattr(self, field_name)

            # Skip None values if requested
            if exclude_none and value is None:
                continue

            # Use alias (explicit or generated)
            key = computed_field.get_serialization_key(alias_generator)
            result[key] = value

        return result

    def json(
        self,
        exclude_none: bool = False,
        exclude_fields: list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        """Serialize model to JSON string.

        Args:
            exclude_none: If True, exclude fields with None values
            exclude_fields: List of field names to exclude from output
            **kwargs: Arguments to pass to json.dumps (indent, default, etc.)
                     Can include a custom 'default' serializer which will be
                     chained with the built-in serializer.

        Returns:
            JSON string representation of the model (including computed fields)
        """
        exclude_fields = exclude_fields or []
        alias_generator = getattr(self.__class__, "_alias_generator", None)

        # Build dict respecting JSON-specific exclusions
        result = {}

        # Add regular fields
        for field_name, (field, _, _) in self._fields.items():
            # Skip if field is in exclude list
            if field_name in exclude_fields:
                continue

            # Skip if field is excluded from JSON
            if field.exclude or field.exclude_from_json:
                continue

            if not hasattr(self, field_name):
                continue

            value = getattr(self, field_name)

            # Skip None values if requested
            if exclude_none and value is None:
                continue

            # Use alias (explicit or generated)
            key = field.get_serialization_key(alias_generator)
            result[key] = value

        # Add computed fields
        computed_fields = getattr(self.__class__, "_computed_fields", {})
        for field_name, computed_field in computed_fields.items():
            # Skip if field is in exclude list
            if field_name in exclude_fields:
                continue

            value = getattr(self, field_name)

            # Skip None values if requested
            if exclude_none and value is None:
                continue

            # Use alias (explicit or generated)
            key = computed_field.get_serialization_key(alias_generator)
            result[key] = value

        # Use custom serializer from kwargs, fallback to Config, then default
        custom_serializer = kwargs.pop("default", None)
        if custom_serializer is None:
            custom_serializer = getattr(self.__class__, "_json_serializer", None)
        serializer = create_json_serializer(custom_serializer)
        return json.dumps(result, default=serializer, **kwargs)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create model instance from dictionary.

        Supports both field names and aliases for input keys.

        Args:
            data: Dictionary with field values

        Returns:
            New model instance

        Raises:
            ValidationError: If validation fails
        """
        # Map aliases back to field names
        mapped_data = {}
        for key, value in data.items():
            # Find the field by name or alias
            field_name = cls._find_field_by_key(key)
            if field_name:
                mapped_data[field_name] = value
            else:
                # Unknown key - pass through (will be caught by validation if required)
                mapped_data[key] = value

        return cls(**mapped_data)

    @classmethod
    def _find_field_by_key(cls, key: str) -> str | None:
        """Find field name by either field name or alias (explicit or generated)."""
        alias_generator = getattr(cls, "_alias_generator", None)

        for field_name, (field, _, _) in cls._fields.items():
            # Check exact field name match
            if field_name == key:
                return field_name

            # Check explicit alias
            if field.alias == key:
                return field_name

            # Check generated alias
            if alias_generator:
                generated_alias = alias_generator(field_name)
                if generated_alias == key:
                    return field_name

        return None

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
