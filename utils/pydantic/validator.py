"""Pydantic validator factory methods for common field validations."""

import re
from collections.abc import Callable
from typing import Any

# Import standalone Validator for reusing validation logic
from utils.validator import Validator as StandaloneValidator


class Validator:
    """Static utility class for creating Pydantic field validators."""

    @staticmethod
    def email(*, error_message: str = "Invalid email format") -> Callable[[str], str]:
        """Create validator for email address format.

        Args:
            error_message: Custom error message (keyword-only)

        Returns:
            Validator function that checks email format

        Example:
            ```python
            from pydantic import BaseModel
            from typing import Annotated
            from pydantic import AfterValidator
            from utils import PydanticValidator

            class User(BaseModel):
                email: Annotated[str, AfterValidator(PydanticValidator.email())]
            ```
        """

        def validate(value: str) -> str:
            if not StandaloneValidator.email(value):
                raise ValueError(error_message)
            return value

        return validate

    @staticmethod
    def url(*, error_message: str = "Invalid URL format") -> Callable[[str], str]:
        """Create validator for URL format.

        Args:
            error_message: Custom error message (keyword-only)

        Returns:
            Validator function that checks URL format

        Example:
            ```python
            from pydantic import BaseModel
            from typing import Annotated
            from pydantic import AfterValidator
            from utils import PydanticValidator

            class Resource(BaseModel):
                url: Annotated[str, AfterValidator(PydanticValidator.url())]
            ```
        """

        def validate(value: str) -> str:
            if not StandaloneValidator.url(value):
                raise ValueError(error_message)
            return value

        return validate

    @staticmethod
    def phone(*, error_message: str = "Invalid phone number") -> Callable[[str], str]:
        """Create validator for phone number (10-15 digits).

        Args:
            error_message: Custom error message (keyword-only)

        Returns:
            Validator function that checks phone number format

        Example:
            ```python
            from pydantic import BaseModel
            from typing import Annotated
            from pydantic import AfterValidator
            from utils import PydanticValidator

            class Contact(BaseModel):
                phone: Annotated[str, AfterValidator(PydanticValidator.phone())]
            ```
        """

        def validate(value: str) -> str:
            if not StandaloneValidator.phone(value):
                raise ValueError(error_message)
            return value

        return validate

    @staticmethod
    def min_length(*, length: int, error_message: str | None = None) -> Callable[[str], str]:
        """Create validator for minimum string length.

        Args:
            length: Minimum allowed length (keyword-only)
            error_message: Custom error message (keyword-only)

        Returns:
            Validator function that checks minimum length

        Example:
            ```python
            from pydantic import BaseModel
            from typing import Annotated
            from pydantic import AfterValidator
            from utils import PydanticValidator

            class User(BaseModel):
                username: Annotated[str, AfterValidator(PydanticValidator.min_length(length=3))]
            ```
        """
        if error_message is None:
            error_message = f"String must be at least {length} characters long"

        def validate(value: str) -> str:
            if len(value) < length:
                raise ValueError(error_message)
            return value

        return validate

    @staticmethod
    def max_length(*, length: int, error_message: str | None = None) -> Callable[[str], str]:
        """Create validator for maximum string length.

        Args:
            length: Maximum allowed length (keyword-only)
            error_message: Custom error message (keyword-only)

        Returns:
            Validator function that checks maximum length

        Example:
            ```python
            from pydantic import BaseModel
            from typing import Annotated
            from pydantic import AfterValidator
            from utils import PydanticValidator

            class User(BaseModel):
                bio: Annotated[str, AfterValidator(PydanticValidator.max_length(length=500))]
            ```
        """
        if error_message is None:
            error_message = f"String must be at most {length} characters long"

        def validate(value: str) -> str:
            if len(value) > length:
                raise ValueError(error_message)
            return value

        return validate

    @staticmethod
    def length_range(
        *, min_length: int, max_length: int, error_message: str | None = None
    ) -> Callable[[str], str]:
        """Create validator for string length range.

        Args:
            min_length: Minimum allowed length (keyword-only)
            max_length: Maximum allowed length (keyword-only)
            error_message: Custom error message (keyword-only)

        Returns:
            Validator function that checks length is within range

        Example:
            ```python
            from pydantic import BaseModel
            from typing import Annotated
            from pydantic import AfterValidator
            from utils import PydanticValidator

            class User(BaseModel):
                password: Annotated[str, AfterValidator(
                    PydanticValidator.length_range(min_length=8, max_length=128)
                )]
            ```
        """
        if error_message is None:
            error_message = f"String must be between {min_length} and {max_length} characters long"

        def validate(value: str) -> str:
            if not (min_length <= len(value) <= max_length):
                raise ValueError(error_message)
            return value

        return validate

    @staticmethod
    def regex_pattern(*, pattern: str, error_message: str | None = None) -> Callable[[str], str]:
        """Create validator for regex pattern matching.

        Args:
            pattern: Regular expression pattern (keyword-only)
            error_message: Custom error message (keyword-only)

        Returns:
            Validator function that checks pattern match

        Example:
            ```python
            from pydantic import BaseModel
            from typing import Annotated
            from pydantic import AfterValidator
            from utils import PydanticValidator

            class User(BaseModel):
                username: Annotated[str, AfterValidator(
                    PydanticValidator.regex_pattern(pattern=r'^[a-zA-Z0-9_]+$')
                )]
            ```
        """
        if error_message is None:
            error_message = f"String must match pattern: {pattern}"

        def validate(value: str) -> str:
            if not re.match(pattern, value):
                raise ValueError(error_message)
            return value

        return validate

    @staticmethod
    def choices(*, options: list[Any], error_message: str | None = None) -> Callable[[Any], Any]:
        """Create validator for allowed choices.

        Args:
            options: List of allowed values (keyword-only)
            error_message: Custom error message (keyword-only)

        Returns:
            Validator function that checks value is in allowed options

        Example:
            ```python
            from pydantic import BaseModel
            from typing import Annotated
            from pydantic import AfterValidator
            from utils import PydanticValidator

            class User(BaseModel):
                role: Annotated[str, AfterValidator(
                    PydanticValidator.choices(options=['admin', 'user', 'guest'])
                )]
            ```
        """
        if error_message is None:
            error_message = f"Value must be one of: {', '.join(str(o) for o in options)}"

        def validate(value: Any) -> Any:
            if value not in options:
                raise ValueError(error_message)
            return value

        return validate

    @staticmethod
    def numeric_range(
        *,
        min_value: float | None = None,
        max_value: float | None = None,
        error_message: str | None = None,
    ) -> Callable[[float | int], float | int]:
        """Create validator for numeric range.

        Args:
            min_value: Minimum allowed value (keyword-only, optional)
            max_value: Maximum allowed value (keyword-only, optional)
            error_message: Custom error message (keyword-only)

        Returns:
            Validator function that checks numeric value is within range

        Example:
            ```python
            from pydantic import BaseModel
            from typing import Annotated
            from pydantic import AfterValidator
            from utils import PydanticValidator

            class Product(BaseModel):
                price: Annotated[float, AfterValidator(
                    PydanticValidator.numeric_range(min_value=0.0, max_value=1000000.0)
                )]
            ```
        """
        if error_message is None:
            if min_value is not None and max_value is not None:
                error_message = f"Value must be between {min_value} and {max_value}"
            elif min_value is not None:
                error_message = f"Value must be at least {min_value}"
            elif max_value is not None:
                error_message = f"Value must be at most {max_value}"
            else:
                error_message = "Value is out of range"

        def validate(value: float | int) -> float | int:
            if min_value is not None and value < min_value:
                raise ValueError(error_message)
            if max_value is not None and value > max_value:
                raise ValueError(error_message)
            return value

        return validate

    @staticmethod
    def list_min_length(*, length: int, error_message: str | None = None) -> Callable[[list], list]:
        """Create validator for minimum list length.

        Args:
            length: Minimum allowed list length (keyword-only)
            error_message: Custom error message (keyword-only)

        Returns:
            Validator function that checks minimum list length

        Example:
            ```python
            from pydantic import BaseModel
            from typing import Annotated
            from pydantic import AfterValidator
            from utils import PydanticValidator

            class Team(BaseModel):
                members: Annotated[list[str], AfterValidator(
                    PydanticValidator.list_min_length(length=1)
                )]
            ```
        """
        if error_message is None:
            error_message = f"List must contain at least {length} items"

        def validate(value: list) -> list:
            if len(value) < length:
                raise ValueError(error_message)
            return value

        return validate

    @staticmethod
    def list_max_length(*, length: int, error_message: str | None = None) -> Callable[[list], list]:
        """Create validator for maximum list length.

        Args:
            length: Maximum allowed list length (keyword-only)
            error_message: Custom error message (keyword-only)

        Returns:
            Validator function that checks maximum list length

        Example:
            ```python
            from pydantic import BaseModel
            from typing import Annotated
            from pydantic import AfterValidator
            from utils import PydanticValidator

            class Survey(BaseModel):
                answers: Annotated[list[str], AfterValidator(
                    PydanticValidator.list_max_length(length=10)
                )]
            ```
        """
        if error_message is None:
            error_message = f"List must contain at most {length} items"

        def validate(value: list) -> list:
            if len(value) > length:
                raise ValueError(error_message)
            return value

        return validate

    @staticmethod
    def not_empty(*, error_message: str = "Value cannot be empty") -> Callable[[Any], Any]:
        """Create validator that ensures value is not empty.

        Args:
            error_message: Custom error message (keyword-only)

        Returns:
            Validator function that checks value is not empty

        Example:
            ```python
            from pydantic import BaseModel
            from typing import Annotated
            from pydantic import AfterValidator
            from utils import PydanticValidator

            class User(BaseModel):
                name: Annotated[str, AfterValidator(PydanticValidator.not_empty())]
            ```
        """

        def validate(value: Any) -> Any:
            if value is None:
                raise ValueError(error_message)
            if isinstance(value, str) and len(value.strip()) == 0:
                raise ValueError(error_message)
            if isinstance(value, list | dict | tuple | set) and len(value) == 0:
                raise ValueError(error_message)
            return value

        return validate
