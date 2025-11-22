"""Primitive field types for Model system."""

from __future__ import annotations

from typing import Any

from utils.model.exceptions import ValidationError
from utils.model.fields.base import Field


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
