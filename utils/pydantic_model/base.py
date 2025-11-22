"""Base Pydantic Model with transform/validate API."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any, ClassVar, Self

from pydantic import BaseModel, ConfigDict
from pydantic import ValidationError as PydanticValidationError

from utils.pydantic_model.exceptions import ValidationError
from utils.pydantic_model.helpers import call_with_context, normalize_to_list


class PydanticModel(BaseModel):
    """Base model with transform/validate API on top of Pydantic.

    This class extends Pydantic's BaseModel to provide the clean transform/validate
    API from utils.model while leveraging Pydantic's performance and features.

    Example:
        ```python
        from utils.pydantic_model import PydanticModel
        from utils import Validator
        from pydantic import Field

        class User(PydanticModel):
            class Config:
                # Apply transforms to multiple fields
                apply_transforms = {
                    ("email", "username"): [str.strip, str.lower]
                }

                # Apply validators to multiple fields
                apply_validators = {
                    ("email",): Validator.email
                }

                # Global validators with cross-field logic
                global_validators = [
                    lambda vals: vals["age"] >= 18 or vals["role"] != "admin"
                ]

                # Extra fields handling: "store" (default), "strict", or "ignore"
                extra_fields_mode = "store"

                # Custom JSON serializer
                json_serializer = custom_serializer_function

            email: str
            username: str
            age: int = Field(ge=0, le=120)
            role: str = "user"
        ```
    """

    model_config = ConfigDict(
        validate_assignment=True,  # Re-validate on field assignment
        arbitrary_types_allowed=True,  # Allow custom types
        extra="allow",  # Allow extra fields by default
    )

    # Metadata storage (set by metaclass/model initialization)
    _field_transforms: ClassVar[dict[str, list]] = {}
    _field_validators: ClassVar[dict[str, list]] = {}
    _global_validators: ClassVar[list[Callable]] = []
    _json_serializer: ClassVar[Callable[[Any], Any] | None] = None

    def __init__(self, **data: Any):
        """Initialize model with transforms and validation.

        Args:
            **data: Field values

        Raises:
            ValidationError: If validation fails
        """
        # Apply transforms before Pydantic validation
        transformed_data = self._apply_transforms(data)

        try:
            # Initialize Pydantic model
            super().__init__(**transformed_data)

            # Apply custom validators after Pydantic validation
            self._apply_custom_validators()

            # Run global validators
            self._run_global_validators()
        except PydanticValidationError as e:
            raise ValidationError.from_pydantic(e) from e

    def _apply_transforms(self, data: dict[str, Any]) -> dict[str, Any]:
        """Apply transforms to input data.

        Args:
            data: Input field values

        Returns:
            Transformed field values
        """
        if not hasattr(self.__class__, "_field_transforms"):
            return data

        transformed = data.copy()
        transforms = getattr(self.__class__, "_field_transforms", {})

        for field_name, transform_list in transforms.items():
            if field_name not in transformed:
                continue

            value = transformed[field_name]
            if value is None:
                continue

            # Apply each transform in sequence
            for transform_spec in transform_list:
                # Handle (func, kwargs) tuple
                if isinstance(transform_spec, tuple):
                    func, kwargs = transform_spec
                    value = call_with_context(func, value, kwargs, transformed)
                else:
                    value = call_with_context(transform_spec, value, {}, transformed)

            transformed[field_name] = value

        return transformed

    def _apply_custom_validators(self) -> None:
        """Apply custom validators to fields.

        Raises:
            ValidationError: If validation fails
        """
        if not hasattr(self.__class__, "_field_validators"):
            return

        validators = getattr(self.__class__, "_field_validators", {})
        all_values = self.model_dump()

        for field_name, validator_list in validators.items():
            if not hasattr(self, field_name):
                continue

            value = getattr(self, field_name)
            if value is None:
                continue

            # Apply each validator
            for validator_spec in validator_list:
                # Handle (func, kwargs) tuple
                if isinstance(validator_spec, tuple):
                    func, kwargs = validator_spec
                else:
                    func, kwargs = validator_spec, {}

                try:
                    result = call_with_context(func, value, kwargs, all_values)
                    if result is False:
                        raise ValidationError(f"Validation failed for field '{field_name}'")
                except ValidationError:
                    raise
                except Exception as e:
                    raise ValidationError(
                        f"Validation error for field '{field_name}': {e}"
                    ) from e

    def _run_global_validators(self) -> None:
        """Run global validators with all field values.

        Raises:
            ValidationError: If validation fails
        """
        if not hasattr(self.__class__, "_global_validators"):
            return

        validators = getattr(self.__class__, "_global_validators", [])
        all_values = self.model_dump()

        for validator in validators:
            try:
                result = validator(all_values)
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

    def to_dict(
        self, *, exclude_none: bool = False, exclude_fields: list[str] | None = None
    ) -> dict[str, Any]:
        """Convert model to dictionary.

        Args:
            exclude_none: If True, exclude fields with None values
            exclude_fields: List of field names to exclude

        Returns:
            Dictionary representation
        """
        data = self.model_dump(exclude_none=exclude_none)

        if exclude_fields:
            for field in exclude_fields:
                data.pop(field, None)

        return data

    def json(
        self,
        *,
        exclude_none: bool = False,
        exclude_fields: list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        """Serialize model to JSON string.

        Args:
            exclude_none: If True, exclude fields with None values
            exclude_fields: List of field names to exclude
            **kwargs: Additional arguments for json.dumps

        Returns:
            JSON string
        """
        data = self.to_dict(exclude_none=exclude_none, exclude_fields=exclude_fields)

        # Use custom serializer if provided
        custom_serializer = kwargs.pop("default", None)
        if custom_serializer is None:
            custom_serializer = getattr(self.__class__, "_json_serializer", None)

        if custom_serializer:
            # Chain with Pydantic's serializer
            from utils.model.serialization import create_json_serializer

            serializer = create_json_serializer(custom_serializer)
            return json.dumps(data, default=serializer, **kwargs)

        # Use Pydantic's serialization
        return self.model_dump_json(exclude_none=exclude_none, **kwargs)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create model from dictionary.

        Args:
            data: Dictionary with field values

        Returns:
            Model instance

        Raises:
            ValidationError: If validation fails
        """
        try:
            return cls(**data)
        except ValidationError:
            raise
        except PydanticValidationError as e:
            raise ValidationError.from_pydantic(e) from e

    @classmethod
    def model_validate(cls, data: dict[str, Any]) -> Self:
        """Pydantic-compatible alias for from_dict.

        Args:
            data: Dictionary with field values

        Returns:
            Model instance
        """
        return cls.from_dict(data)

    @classmethod
    def model_validate_json(cls, json_data: str) -> Self:
        """Create model from JSON string.

        Args:
            json_data: JSON string

        Returns:
            Model instance

        Raises:
            ValidationError: If validation fails
        """
        try:
            data = json.loads(json_data)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON: {e}") from e

    def __init_subclass__(cls, **kwargs: Any):
        """Process subclass to set up transforms/validators.

        This method processes the Config class and field annotations
        to set up the transform/validate infrastructure.
        """
        super().__init_subclass__(**kwargs)

        # Extract Config class
        config = getattr(cls, "Config", None)
        if config is None:
            return

        # Extract transforms, validators, and other config
        cls._field_transforms = {}
        cls._field_validators = {}
        cls._global_validators = getattr(config, "global_validators", [])
        cls._json_serializer = getattr(config, "json_serializer", None)

        # Process apply_transforms
        apply_transforms = getattr(config, "apply_transforms", {})
        for field_names, transforms in apply_transforms.items():
            transform_list = normalize_to_list(transforms)
            for field_name in field_names:
                if field_name not in cls._field_transforms:
                    cls._field_transforms[field_name] = []
                cls._field_transforms[field_name].extend(transform_list)

        # Process apply_validators
        apply_validators = getattr(config, "apply_validators", {})
        for field_names, validators in apply_validators.items():
            validator_list = normalize_to_list(validators)
            for field_name in field_names:
                if field_name not in cls._field_validators:
                    cls._field_validators[field_name] = []
                cls._field_validators[field_name].extend(validator_list)

        # Merge Pydantic ConfigDict if present
        config_dict = getattr(config, "config_dict", {})
        if config_dict:
            cls.model_config = ConfigDict(**{**cls.model_config, **config_dict})

        # Handle extra_fields_mode
        extra_mode = getattr(config, "extra_fields_mode", None)
        if extra_mode:
            mode_map = {"store": "allow", "strict": "forbid", "ignore": "ignore"}
            if extra_mode in mode_map:
                cls.model_config = ConfigDict(**{**cls.model_config, "extra": mode_map[extra_mode]})
