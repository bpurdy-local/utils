"""Test extra_fields_mode functionality."""

import pytest

from utils.pydantic_model import PydanticModel, ValidationError


def test_extra_fields_store_mode():
    """Test store mode (default) - stores extra fields."""

    class User(PydanticModel):
        class Config:
            extra_fields_mode = "store"

        name: str
        age: int

    user = User(name="Alice", age=25, role="admin", department="Engineering")

    # Extra fields should be accessible
    assert user.role == "admin"
    assert user.department == "Engineering"

    # Should appear in dict
    data = user.to_dict()
    assert data["role"] == "admin"
    assert data["department"] == "Engineering"


def test_extra_fields_default_is_store():
    """Test that store mode is the default."""

    class User(PydanticModel):
        name: str
        age: int

    user = User(name="Alice", age=25, extra_field="value")

    # Should be accessible (store is default)
    assert user.extra_field == "value"


def test_extra_fields_strict_mode():
    """Test strict mode - raises error on extra fields."""

    class User(PydanticModel):
        class Config:
            extra_fields_mode = "strict"

        name: str
        age: int

    # Should raise error with extra fields
    with pytest.raises(ValidationError):
        User(name="Alice", age=25, role="admin")

    # Should work without extra fields
    user = User(name="Alice", age=25)
    assert user.name == "Alice"


def test_extra_fields_ignore_mode():
    """Test ignore mode - silently ignores extra fields."""

    class User(PydanticModel):
        class Config:
            extra_fields_mode = "ignore"

        name: str
        age: int

    # Should not raise error
    user = User(name="Alice", age=25, role="admin", department="Engineering")

    # Extra fields should not be accessible
    assert not hasattr(user, "role")
    assert not hasattr(user, "department")

    # Should not appear in dict
    data = user.to_dict()
    assert "role" not in data
    assert "department" not in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
