"""ModelField for nested Model instances."""

from __future__ import annotations

from typing import Any, TypeVar

from utils.model.exceptions import ValidationError
from utils.model.fields.base import Field

T = TypeVar("T")


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
