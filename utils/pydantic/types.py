"""Pydantic field factory methods for creating custom field types with transformations."""

from collections.abc import Callable
from typing import Annotated, Any

from pydantic import AfterValidator, BeforeValidator


class Field:
    """Static utility class for creating Pydantic field types with transformations and validators.

    Provides common string transforms and a flexible field() method to combine
    transforms with validators.
    """

    # Common string transforms - simple lambdas wrapping built-in str methods
    # These provide clean syntax without repetitive lambdas in user code
    strip = staticmethod(lambda value: value.strip())
    lower = staticmethod(lambda value: value.lower())
    upper = staticmethod(lambda value: value.upper())
    title = staticmethod(lambda value: value.title())
    capitalize = staticmethod(lambda value: value.capitalize())

    @staticmethod
    def field(
        base_type: type = str,
        *,
        transforms: Callable[[Any], Any] | list[Callable[[Any], Any]] | None = None,
        validators: Callable[[Any], Any] | list[Callable[[Any], Any]] | None = None,
        skip_none: bool = True,
    ) -> Any:
        """Create a Pydantic field type with both transforms and validators.

        This is a convenience method that combines transforms (applied before type coercion)
        and validators (applied after type coercion) into a single field type.

        Args:
            base_type: The base type for the field (default: str)
            transforms: Transform function(s) to apply before validation (keyword-only)
            validators: Validator function(s) to apply after type coercion (keyword-only)
            skip_none: If True, skip transforms when value is None (keyword-only, default True)

        Returns:
            Annotated type that can be used as a field type hint

        Example:
            ```python
            from pydantic import BaseModel
            from utils import PydanticField, PydanticValidator

            # Combine transforms and validators (no lambdas needed!)
            class User(BaseModel):
                email: PydanticField.field(
                    transforms=[PydanticField.strip, PydanticField.lower],
                    validators=PydanticValidator.email()
                )

            user = User(email="  Test@EXAMPLE.COM  ")
            assert user.email == "test@example.com"

            # Multiple validators
            class User(BaseModel):
                username: PydanticField.field(
                    transforms=PydanticField.strip,
                    validators=[
                        PydanticValidator.min_length(length=3),
                        PydanticValidator.max_length(length=20)
                    ]
                )

            # Custom transforms when you need arguments
            from utils import Integer
            class Product(BaseModel):
                quantity: PydanticField.field(
                    base_type=int,
                    transforms=lambda x: Integer.clamp(x, min_val=0, max_val=100)
                )
            ```
        """
        annotations = []

        # Add transforms as BeforeValidator
        if transforms is not None:
            transform_list = transforms if isinstance(transforms, list) else [transforms]

            def apply_transforms(value: Any) -> Any:
                """Apply all transforms in sequence."""
                if skip_none and value is None:
                    return value

                result = value
                for transform_fn in transform_list:
                    try:
                        result = transform_fn(result)
                    except Exception as e:
                        raise ValueError(f"Transform {transform_fn.__name__} failed: {e}") from e

                return result

            annotations.append(BeforeValidator(apply_transforms))

        # Add validators as AfterValidator
        if validators is not None:
            validator_list = validators if isinstance(validators, list) else [validators]
            for validator_fn in validator_list:
                annotations.append(AfterValidator(validator_fn))

        # Return annotated type
        if annotations:
            return Annotated[base_type, *annotations]
        return base_type
