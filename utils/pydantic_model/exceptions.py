"""Exceptions for Pydantic Model system."""

from pydantic import ValidationError as PydanticValidationError


class ValidationError(ValueError):
    """Validation error raised when field validation fails.

    This wraps Pydantic's ValidationError to maintain API compatibility
    with the original utils.model system.
    """

    def __init__(self, message: str, pydantic_error: PydanticValidationError | None = None):
        """Initialize validation error.

        Args:
            message: Human-readable error message
            pydantic_error: Optional underlying Pydantic validation error
        """
        super().__init__(message)
        self.pydantic_error = pydantic_error

    @classmethod
    def from_pydantic(cls, error: PydanticValidationError) -> "ValidationError":
        """Create ValidationError from Pydantic ValidationError.

        Args:
            error: Pydantic validation error

        Returns:
            ValidationError instance
        """
        # Extract first error message for compatibility
        if error.errors():
            first_error = error.errors()[0]
            msg = first_error.get("msg", str(error))
            return cls(msg, error)
        return cls(str(error), error)
