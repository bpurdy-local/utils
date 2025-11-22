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
    """Raised when field validation fails.

    Attributes:
        errors: List of validation errors with field names and messages
    """

    def __init__(self, message: str, errors: list[dict[str, str]] | None = None):
        super().__init__(message)
        self.errors = errors or []

    def add_error(self, field: str, message: str) -> None:
        """Add a validation error for a specific field."""
        self.errors.append({"field": field, "message": message})

    def __str__(self) -> str:
        """Return formatted error message with all field errors."""
        if not self.errors:
            return super().__str__()

        error_lines = [super().__str__()]
        for error in self.errors:
            error_lines.append(f"  - {error['field']}: {error['message']}")
        return "\n".join(error_lines)


# ============================================================================
# Computed Field Decorator
# ============================================================================


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


# ============================================================================
# Alias Generator Helper Functions
# ============================================================================


def to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase.

    Args:
        snake_str: String in snake_case format

    Returns:
        String in camelCase format
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


# ============================================================================
# Helper Functions for Callable Execution
# ============================================================================


def _function_accepts_param(func: Callable, param_name: str) -> bool:
    """Check if a function accepts a specific parameter."""
    sig = inspect.signature(func)
    return param_name in sig.parameters


def _call_with_context(func: Callable, value: Any, all_values: dict[str, Any], kwargs: dict) -> Any:
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
        self.transforms = _normalize_to_list(transform)
        self.validators = _normalize_to_list(validate)
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
        from utils.convert import Convert

        result = Convert.to_bool(value)
        if result is None:
            if isinstance(value, str):
                raise ValidationError(
                    f"Field '{self.name}' cannot convert string {value!r} to bool"
                )
            raise ValidationError(f"Field '{self.name}' cannot convert {value!r} to bool")
        return result


class ListField(Field[list]):
    """Field for list values with optional item validation."""

    def __init__(
        self,
        *,
        item_type: type | None = None,
        item_validator: Callable | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.item_type = item_type
        self.item_validator = item_validator
        self.min_length = min_length
        self.max_length = max_length

    def __set__(self, obj: Any, value: Any) -> None:
        """Validate list and its items."""
        if value is None and not self.required:
            obj.__dict__[self.name] = None
            return

        if not isinstance(value, list):
            raise ValidationError(f"Field '{self.name}' must be a list, got {type(value).__name__}")

        # Validate length
        if self.min_length is not None and len(value) < self.min_length:
            raise ValidationError(f"Field '{self.name}' must have at least {self.min_length} items")
        if self.max_length is not None and len(value) > self.max_length:
            raise ValidationError(f"Field '{self.name}' must have at most {self.max_length} items")

        # Validate items
        validated_items = []
        for i, item in enumerate(value):
            validated_item = self._validate_item(item, i)
            validated_items.append(validated_item)

        # Set the validated list
        obj.__dict__[self.name] = validated_items

    def _validate_item(self, item: Any, index: int) -> Any:
        """Validate a single list item."""
        # Type validation
        if self.item_type is not None and not isinstance(item, self.item_type):
            # Try to convert if it's a Model class
            if isinstance(self.item_type, type) and issubclass(self.item_type, Model):
                if isinstance(item, dict):
                    item = self.item_type.from_dict(item)
                else:
                    raise ValidationError(
                        f"Field '{self.name}[{index}]' must be {self.item_type.__name__}"
                    )
            else:
                raise ValidationError(
                    f"Field '{self.name}[{index}]' must be {self.item_type.__name__}"
                )

        # Custom validation
        if self.item_validator:
            try:
                result = self.item_validator(item)
                if result is False:
                    raise ValidationError(f"Field '{self.name}[{index}]' failed validation")
            except ValidationError:
                raise
            except Exception as e:
                raise ValidationError(f"Field '{self.name}[{index}]' validation error: {e}") from e

        return item


class DictField(Field[dict]):
    """Field for dict values with optional key/value validation."""

    def __init__(
        self,
        *,
        key_type: type | None = None,
        value_type: type | None = None,
        value_validator: Callable | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.key_type = key_type
        self.value_type = value_type
        self.value_validator = value_validator

    def __set__(self, obj: Any, value: Any) -> None:
        """Validate dict and its keys/values."""
        if value is None and not self.required:
            obj.__dict__[self.name] = None
            return

        if not isinstance(value, dict):
            raise ValidationError(f"Field '{self.name}' must be a dict, got {type(value).__name__}")

        # Validate keys and values
        validated_dict = {}
        for key, val in value.items():
            validated_key = self._validate_key(key)
            validated_val = self._validate_value(val, key)
            validated_dict[validated_key] = validated_val

        obj.__dict__[self.name] = validated_dict

    def _validate_key(self, key: Any) -> Any:
        """Validate a dictionary key."""
        if self.key_type is not None and not isinstance(key, self.key_type):
            raise ValidationError(f"Field '{self.name}' keys must be {self.key_type.__name__}")
        return key

    def _validate_value(self, value: Any, key: Any) -> Any:
        """Validate a dictionary value."""
        # Type validation
        if self.value_type is not None and not isinstance(value, self.value_type):
            # Try to convert if it's a Model class
            if isinstance(self.value_type, type) and issubclass(self.value_type, Model):
                if isinstance(value, dict):
                    value = self.value_type.from_dict(value)
                else:
                    raise ValidationError(
                        f"Field '{self.name}[{key!r}]' must be {self.value_type.__name__}"
                    )
            else:
                raise ValidationError(
                    f"Field '{self.name}[{key!r}]' must be {self.value_type.__name__}"
                )

        # Custom validation
        if self.value_validator:
            try:
                result = self.value_validator(value)
                if result is False:
                    raise ValidationError(f"Field '{self.name}[{key!r}]' failed validation")
            except ValidationError:
                raise
            except Exception as e:
                raise ValidationError(f"Field '{self.name}[{key!r}]' validation error: {e}") from e

        return value


class ModelField(Field[T]):
    """Field for nested Model instances with automatic dict conversion."""

    def __init__(self, model_class: type[T], **kwargs):
        super().__init__(**kwargs)
        self.model_class = model_class

    def __set__(self, obj: Any, value: Any) -> None:
        """Convert dict to Model instance if needed."""
        if value is None and not self.required:
            obj.__dict__[self.name] = None
            return

        # Convert dict to Model instance
        if isinstance(value, dict):
            try:
                value = self.model_class.from_dict(value)
            except Exception as e:
                raise ValidationError(
                    f"Field '{self.name}' failed to create {self.model_class.__name__}: {e}"
                ) from e
        elif not isinstance(value, self.model_class):
            raise ValidationError(
                f"Field '{self.name}' must be {self.model_class.__name__} or dict"
            )

        obj.__dict__[self.name] = value


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

        # Extract Config class if present
        config_class = namespace.get("Config")
        alias_generator = None
        apply_transforms = {}
        apply_validators = {}
        global_validators = []
        extra_fields_mode = "store"  # Default: store unknown fields

        if config_class:
            alias_generator = getattr(config_class, "alias_generator", None)
            apply_transforms = getattr(config_class, "apply_transforms", {})
            apply_validators = getattr(config_class, "apply_validators", {})
            global_validators = getattr(config_class, "global_validators", [])
            extra_fields_mode = getattr(config_class, "extra_fields_mode", "store")

        # Process all field annotations
        fields = mcs._collect_fields(namespace)

        # Apply bulk transforms and validators
        _apply_bulk_transforms(fields, apply_transforms)
        _apply_bulk_validators(fields, apply_validators)

        # Collect computed fields
        computed_fields = mcs._collect_computed_fields(namespace)

        # Store metadata on class
        cls._fields = fields
        cls._computed_fields = computed_fields
        cls._global_validators = global_validators
        cls._alias_generator = alias_generator
        cls._extra_fields_mode = extra_fields_mode

        # Set field descriptors as class attributes
        for field_name, (field_instance, _, _) in fields.items():
            # Manually call __set_name__ for auto-created fields
            if field_instance.name is None:
                field_instance.__set_name__(cls, field_name)
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

    @staticmethod
    def _collect_computed_fields(namespace: dict) -> dict[str, ComputedFieldDescriptor]:
        """Collect all computed field descriptors."""
        computed_fields = {}
        for name, value in namespace.items():
            if isinstance(value, ComputedFieldDescriptor):
                computed_fields[name] = value
        return computed_fields


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
                raise ValidationError(
                    f"Unknown field(s) provided: {fields_list}"
                )
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

        custom_serializer = kwargs.pop("default", None)
        serializer = _create_json_serializer(custom_serializer)
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


__all__ = [
    "Model",
    "Field",
    "StringField",
    "IntField",
    "FloatField",
    "BoolField",
    "ListField",
    "DictField",
    "ModelField",
    "ValidationError",
    "computed_field",
    "to_camel",
]
