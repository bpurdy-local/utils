"""Container field types (list, dict) for Model system."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from utils.model.exceptions import ValidationError
from utils.model.fields.base import Field


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
        # Avoid circular import
        from utils.model.model import Model

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
        # Avoid circular import
        from utils.model.model import Model

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
