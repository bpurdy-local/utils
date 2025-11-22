"""Test that native Pydantic features still work correctly."""

from datetime import datetime

import pytest
from pydantic import Field, computed_field, field_validator, model_validator

from utils.pydantic_model import PydanticModel, ValidationError


class TestNativePydanticValidators:
    """Test that Pydantic's @field_validator and @model_validator work."""

    def test_field_validator_decorator(self):
        """Test Pydantic's @field_validator still works."""

        class User(PydanticModel):
            name: str
            age: int

            @field_validator("age")
            @classmethod
            def validate_age(cls, v):
                if v < 0 or v > 120:
                    raise ValueError("Age must be between 0 and 120")
                return v

        # Valid
        user = User(name="Alice", age=25)
        assert user.age == 25

        # Invalid
        with pytest.raises(ValidationError):
            User(name="Alice", age=150)

    def test_model_validator_decorator(self):
        """Test Pydantic's @model_validator still works."""

        class User(PydanticModel):
            password: str
            confirm_password: str

            @model_validator(mode="after")
            def validate_passwords_match(self):
                if self.password != self.confirm_password:
                    raise ValueError("Passwords must match")
                return self

        # Valid
        user = User(password="secret", confirm_password="secret")
        assert user.password == "secret"

        # Invalid
        with pytest.raises(ValidationError):
            User(password="secret", confirm_password="different")

    def test_field_validator_with_config_validators(self):
        """Test that both Pydantic validators and Config validators work together."""

        class User(PydanticModel):
            class Config:
                apply_validators = {
                    ("name",): lambda x: len(x) > 0  # Our validator
                }

            name: str
            age: int

            @field_validator("age")
            @classmethod
            def validate_age(cls, v):
                if v < 0:
                    raise ValueError("Age must be positive")
                return v

        # Both validators should run
        user = User(name="Alice", age=25)
        assert user.name == "Alice"
        assert user.age == 25

        # Our validator fails
        with pytest.raises(ValidationError):
            User(name="", age=25)

        # Pydantic validator fails
        with pytest.raises(ValidationError):
            User(name="Alice", age=-5)


class TestNativePydanticFieldConstraints:
    """Test that Pydantic Field constraints work."""

    def test_field_constraints(self):
        """Test Pydantic Field constraints (ge, le, min_length, etc.)."""

        class User(PydanticModel):
            name: str = Field(min_length=1, max_length=50)
            age: int = Field(ge=0, le=120)
            email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")

        # Valid
        user = User(name="Alice", age=25, email="alice@example.com")
        assert user.name == "Alice"

        # Name too short
        with pytest.raises(ValidationError):
            User(name="", age=25, email="alice@example.com")

        # Age out of range
        with pytest.raises(ValidationError):
            User(name="Alice", age=150, email="alice@example.com")

        # Invalid email pattern
        with pytest.raises(ValidationError):
            User(name="Alice", age=25, email="invalid-email")

    def test_field_defaults_and_factory(self):
        """Test that Field default and default_factory work."""

        class User(PydanticModel):
            name: str
            created_at: datetime = Field(default_factory=datetime.now)
            tags: list[str] = Field(default_factory=list)
            role: str = Field(default="user")

        user1 = User(name="Alice")
        assert user1.role == "user"
        assert user1.tags == []
        assert isinstance(user1.created_at, datetime)

        user2 = User(name="Bob", tags=["admin"], role="admin")
        assert user2.tags == ["admin"]
        assert user2.role == "admin"

    def test_field_alias(self):
        """Test that Field alias works."""

        class User(PydanticModel):
            name: str = Field(alias="userName")
            email: str = Field(alias="emailAddress")

        # Should accept aliased names
        user = User(userName="Alice", emailAddress="alice@example.com")
        assert user.name == "Alice"
        assert user.email == "alice@example.com"

        # Should serialize with aliases
        data = user.model_dump(by_alias=True)
        assert data["userName"] == "Alice"
        assert data["emailAddress"] == "alice@example.com"


class TestNativePydanticTypeValidation:
    """Test that Pydantic's type validation still works."""

    def test_type_coercion(self):
        """Test that Pydantic's type coercion works."""

        class User(PydanticModel):
            name: str
            age: int
            score: float
            active: bool

        # Pydantic v2 is stricter - str won't auto-convert from int
        # But numeric types still coerce from strings
        user = User(name="Alice", age="25", score="3.14", active="true")
        assert user.name == "Alice"
        assert user.age == 25
        assert user.score == 3.14
        assert user.active is True

        # Int to str doesn't auto-coerce in Pydantic v2
        with pytest.raises(ValidationError):
            User(name=123, age=25, score=3.14, active=True)

    def test_optional_fields(self):
        """Test that Optional fields work."""

        class User(PydanticModel):
            name: str
            nickname: str | None = None
            age: int | None = None

        user1 = User(name="Alice")
        assert user1.nickname is None
        assert user1.age is None

        user2 = User(name="Bob", nickname="Bobby", age=25)
        assert user2.nickname == "Bobby"
        assert user2.age == 25

    def test_nested_models(self):
        """Test that nested models work."""

        class Address(PydanticModel):
            street: str
            city: str

        class User(PydanticModel):
            name: str
            address: Address

        # Should accept dict and convert to nested model
        user = User(name="Alice", address={"street": "123 Main St", "city": "NYC"})
        assert isinstance(user.address, Address)
        assert user.address.street == "123 Main St"

        # Should accept nested model instance
        address = Address(street="456 Oak Ave", city="LA")
        user2 = User(name="Bob", address=address)
        assert user2.address.city == "LA"


class TestNativePydanticSerialization:
    """Test that Pydantic's serialization methods work."""

    def test_model_dump(self):
        """Test that model_dump works."""

        class User(PydanticModel):
            name: str
            age: int
            role: str = "user"

        user = User(name="Alice", age=25)
        data = user.model_dump()

        assert data == {"name": "Alice", "age": 25, "role": "user"}

    def test_model_dump_json(self):
        """Test that model_dump_json works."""

        class User(PydanticModel):
            name: str
            age: int

        user = User(name="Alice", age=25)
        json_str = user.model_dump_json()

        assert "Alice" in json_str
        assert "25" in json_str

    def test_model_dump_exclude(self):
        """Test that model_dump exclude works."""

        class User(PydanticModel):
            name: str
            age: int
            password: str

        user = User(name="Alice", age=25, password="secret")
        data = user.model_dump(exclude={"password"})

        assert "password" not in data
        assert data["name"] == "Alice"


class TestNativePydanticComputed:
    """Test that Pydantic's @computed_field works."""

    def test_computed_field(self):
        """Test that @computed_field works."""

        class User(PydanticModel):
            first_name: str
            last_name: str

            @computed_field
            @property
            def full_name(self) -> str:
                return f"{self.first_name} {self.last_name}"

        user = User(first_name="Alice", last_name="Smith")
        assert user.full_name == "Alice Smith"

        # Should appear in serialization
        data = user.model_dump()
        assert data["full_name"] == "Alice Smith"


class TestNativePydanticConfigDict:
    """Test that Pydantic's ConfigDict options work."""

    def test_validate_assignment(self):
        """Test that validate_assignment works (enabled by default in PydanticModel)."""
        from pydantic_core import ValidationError as PydanticCoreValidationError

        class User(PydanticModel):
            age: int = Field(ge=0, le=120)

        user = User(age=25)
        user.age = 30  # Should re-validate
        assert user.age == 30

        # Should fail validation on assignment
        # Note: __setattr__ raises PydanticCoreValidationError, not our wrapped ValidationError
        with pytest.raises(PydanticCoreValidationError):
            user.age = 150

    def test_frozen(self):
        """Test that frozen=True works."""
        from pydantic import ConfigDict as PydanticConfigDict
        from pydantic_core import ValidationError as PydanticCoreValidationError

        class User(PydanticModel):
            model_config = PydanticConfigDict(frozen=True)

            name: str
            age: int

        user = User(name="Alice", age=25)

        # Should not allow assignment
        # Note: frozen check raises PydanticCoreValidationError, not our wrapped ValidationError
        with pytest.raises(PydanticCoreValidationError):
            user.age = 30

    def test_str_strip_whitespace(self):
        """Test that str_strip_whitespace works."""
        from pydantic import ConfigDict as PydanticConfigDict

        class User(PydanticModel):
            model_config = PydanticConfigDict(str_strip_whitespace=True)

            name: str

        user = User(name="  Alice  ")
        assert user.name == "Alice"  # Should be stripped


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
