"""Tests for Pydantic Model system.

This test suite mirrors test_model.py to ensure API compatibility between
the pure-Python Model system and the Pydantic-based PydanticModel system.
"""

import pytest

from utils import Integer, String, Validator
from utils.pydantic_model import (
    BoolField,
    FloatField,
    IntField,
    PydanticModel,
    StringField,
    ValidationError,
    computed_field,
)


# Helper functions for testing
def strip(text: str) -> str:
    """Strip whitespace."""
    return text.strip()


def lower(text: str) -> str:
    """Convert to lowercase."""
    return text.lower()


def truncate(text: str, *, length: int) -> str:
    """Truncate to length."""
    return String.truncate(text, length=length, suffix="")


def is_email(text: str) -> bool:
    """Simple email validator."""
    return Validator.email(text)


def in_range(value: int, *, min: int, max: int) -> bool:
    """Check if value is in range."""
    return min <= value <= max


def clamp(value: int, *, min: int, max: int) -> int:
    """Clamp value to range."""
    return Integer.clamp(value, min_val=min, max_val=max)


class TestBasicFields:
    """Test basic field functionality."""

    def test_string_field_basic(self):
        """Test basic StringField."""

        class User(PydanticModel):
            name: str = StringField()

        user = User(name="Alice")
        assert user.name == "Alice"

    def test_int_field_basic(self):
        """Test basic IntField."""

        class User(PydanticModel):
            age: int = IntField()

        user = User(age=25)
        assert user.age == 25

    def test_float_field_basic(self):
        """Test basic FloatField."""

        class User(PydanticModel):
            score: float = FloatField()

        user = User(score=95.5)
        assert user.score == 95.5

    def test_bool_field_basic(self):
        """Test basic BoolField."""

        class User(PydanticModel):
            active: bool = BoolField()

        user = User(active=True)
        assert user.active is True

    def test_multiple_fields(self):
        """Test model with multiple fields."""

        class User(PydanticModel):
            name: str = StringField()
            age: int = IntField()
            score: float = FloatField()

        user = User(name="Alice", age=25, score=95.5)
        assert user.name == "Alice"
        assert user.age == 25
        assert user.score == 95.5


class TestTransforms:
    """Test field transformations."""

    def test_single_transform(self):
        """Test single transform function."""

        class User(PydanticModel):
            name: str = StringField(transform=strip)

        user = User(name="  Alice  ")
        assert user.name == "Alice"

    def test_multiple_transforms(self):
        """Test multiple transforms in sequence."""

        class User(PydanticModel):
            email: str = StringField(transform=[strip, lower])

        user = User(email="  ADMIN@EXAMPLE.COM  ")
        assert user.email == "admin@example.com"

    def test_transform_with_args_tuple(self):
        """Test transform with arguments using tuple syntax."""

        class User(PydanticModel):
            name: str = StringField(transform=[(truncate, {"length": 5})])

        user = User(name="Alexander")
        assert user.name == "Alexa"

    def test_mixed_transforms(self):
        """Test mix of simple and tuple transforms."""

        class User(PydanticModel):
            email: str = StringField(transform=[strip, lower, (truncate, {"length": 10})])

        user = User(email="  ADMIN@EXAMPLE.COM  ")
        assert user.email == "admin@exam"


class TestValidation:
    """Test field validation."""

    def test_simple_validator(self):
        """Test simple validator function."""

        class User(PydanticModel):
            email: str = StringField(validate=is_email)

        user = User(email="admin@example.com")
        assert user.email == "admin@example.com"

    def test_validator_fails(self):
        """Test validator failure raises ValidationError."""

        class User(PydanticModel):
            email: str = StringField(validate=is_email)

        with pytest.raises(ValidationError):
            User(email="not-an-email")

    def test_validator_with_args(self):
        """Test validator with arguments using tuple syntax."""

        class User(PydanticModel):
            age: int = IntField(validate=(in_range, {"min": 0, "max": 120}))

        user = User(age=25)
        assert user.age == 25

    def test_validator_with_args_fails(self):
        """Test validator with args failure."""

        class User(PydanticModel):
            age: int = IntField(validate=(in_range, {"min": 0, "max": 120}))

        with pytest.raises(ValidationError):
            User(age=150)

    def test_transform_before_validate(self):
        """Test that transforms run before validation."""

        class User(PydanticModel):
            email: str = StringField(transform=[strip, lower], validate=is_email)

        # Validator should see transformed value
        user = User(email="  ADMIN@EXAMPLE.COM  ")
        assert user.email == "admin@example.com"


class TestDictConversion:
    """Test dict conversion methods."""

    def test_to_dict(self):
        """Test to_dict method."""

        class User(PydanticModel):
            name: str = StringField()
            age: int = IntField()

        user = User(name="Alice", age=25)
        data = user.to_dict()

        assert data == {"name": "Alice", "age": 25}

    def test_from_dict(self):
        """Test from_dict method."""

        class User(PydanticModel):
            name: str = StringField()
            age: int = IntField()

        user = User.from_dict({"name": "Alice", "age": 25})

        assert user.name == "Alice"
        assert user.age == 25

    def test_model_validate(self):
        """Test model_validate (Pydantic alias)."""

        class User(PydanticModel):
            name: str = StringField()
            age: int = IntField()

        user = User.model_validate({"name": "Alice", "age": 25})

        assert user.name == "Alice"
        assert user.age == 25

    def test_dict_round_trip(self):
        """Test converting to dict and back."""

        class User(PydanticModel):
            name: str = StringField()
            age: int = IntField()
            active: bool = BoolField()

        user1 = User(name="Alice", age=25, active=True)
        data = user1.to_dict()
        user2 = User.from_dict(data)

        assert user1 == user2


class TestComplexExample:
    """Test complex real-world example."""

    def test_user_model(self):
        """Test comprehensive user model."""

        class User(PydanticModel):
            email: str = StringField(transform=[strip, lower], validate=is_email)
            age: int = IntField(validate=(in_range, {"min": 0, "max": 120}))
            name: str | None = None
            role: str = StringField(default="user")

        # Create user with transforms and validation
        user = User(email="  ADMIN@EXAMPLE.COM  ", age=25, name="Alice")

        assert user.email == "admin@example.com"
        assert user.age == 25
        assert user.name == "Alice"
        assert user.role == "user"

        # Dict conversion
        data = user.to_dict()
        user2 = User.from_dict(data)
        assert user == user2

    def test_transform_returns_value(self):
        """Test transform that returns modified value."""

        class User(PydanticModel):
            age: int = IntField(transform=[(clamp, {"min": 0, "max": 120})])

        user = User(age=150)
        assert user.age == 120  # Clamped to max

        user = User(age=-10)
        assert user.age == 0  # Clamped to min


class TestBulkTransformsValidators:
    """Test bulk application of transforms and validators."""

    def test_apply_transforms_to_multiple_fields(self):
        """Test applying transforms to multiple fields at once."""

        class User(PydanticModel):
            class Config:
                apply_transforms = {
                    ("email", "username"): [strip, lower],
                }

            email: str = StringField()
            username: str = StringField()
            bio: str = StringField()

        user = User(email="  ADMIN@EXAMPLE.COM  ", username="  ADMIN  ", bio="Hello")
        assert user.email == "admin@example.com"
        assert user.username == "admin"
        assert user.bio == "Hello"  # Not affected


class TestGlobalValidators:
    """Test global validators with cross-field logic."""

    def test_global_validator_basic(self):
        """Test basic global validator."""

        def validate_consistency(values: dict) -> bool:
            # Simple validation: email and username should match
            email_prefix = values["email"].split("@")[0]
            return email_prefix == values["username"]

        class User(PydanticModel):
            class Config:
                global_validators = [validate_consistency]

            email: str = StringField()
            username: str = StringField()

        # Valid - email prefix matches username
        user = User(email="admin@example.com", username="admin")
        assert user.email == "admin@example.com"

        # Invalid - email prefix doesn't match username
        with pytest.raises(ValidationError):
            User(email="admin@example.com", username="user")


class TestComputedFields:
    """Test computed field functionality."""

    def test_computed_field_basic(self):
        """Test basic computed field."""

        class User(PydanticModel):
            first_name: str = StringField()
            last_name: str = StringField()

            @computed_field
            def full_name(self) -> str:
                return f"{self.first_name} {self.last_name}"

        user = User(first_name="Alice", last_name="Smith")
        assert user.full_name == "Alice Smith"

    def test_computed_field_in_dict(self):
        """Test computed field appears in dict."""

        class User(PydanticModel):
            first_name: str = StringField()
            last_name: str = StringField()

            @computed_field
            def full_name(self) -> str:
                return f"{self.first_name} {self.last_name}"

        user = User(first_name="Alice", last_name="Smith")
        data = user.to_dict()

        assert "full_name" in data
        assert data["full_name"] == "Alice Smith"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
