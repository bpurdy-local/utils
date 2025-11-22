"""Exception classes for Model system."""

from __future__ import annotations


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
