"""Pydantic-based Model system with transform/validate API.

This package provides a Pydantic BaseModel wrapper that preserves the clean
transform/validate API from utils.model while leveraging Pydantic's performance
and ecosystem benefits.

Features:
- Config-based transforms and validators
- Auto-injection of field values into validators/transforms
- Global validators for cross-field logic
- Compatible with all Pydantic features (Field, computed_field, etc.)
"""

from utils.pydantic_model.base import PydanticModel
from utils.pydantic_model.exceptions import ValidationError

__all__ = [
    "PydanticModel",
    "ValidationError",
]
