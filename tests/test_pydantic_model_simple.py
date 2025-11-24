"""Test simplified Config-based PydanticModel."""

import pytest

from utils.pydantic_model import PydanticModel, ValidationError


class TestConfigBasedTransforms:
    """Test Config-based transform functionality."""

    def test_simple_transform(self):
        """Test single field transform."""

        class User(PydanticModel):
            class Config:
                apply_transforms = {("email",): [str.strip, str.lower]}

            email: str
            age: int

        user = User(email="  ADMIN@EXAMPLE.COM  ", age=25)
        assert user.email == "admin@example.com"
        assert user.age == 25

    def test_multiple_field_transforms(self):
        """Test transforms on multiple fields."""

        class User(PydanticModel):
            class Config:
                apply_transforms = {("email", "username"): [str.strip, str.lower]}

            email: str
            username: str
            age: int

        user = User(email="  ADMIN@EXAMPLE.COM  ", username="  ADMIN  ", age=25)
        assert user.email == "admin@example.com"
        assert user.username == "admin"
        assert user.age == 25

    def test_transform_chain(self):
        """Test multiple transforms in sequence."""

        class Article(PydanticModel):
            class Config:
                apply_transforms = {
                    ("slug",): [str.strip, str.lower, lambda s: s.replace(" ", "-")]
                }

            slug: str

        article = Article(slug="  Hello World  ")
        assert article.slug == "hello-world"

    def test_transform_with_args(self):
        """Test transform with additional arguments."""

        def truncate(text: str, max_length: int) -> str:
            return text[:max_length]

        class Article(PydanticModel):
            class Config:
                apply_transforms = {("summary",): [(truncate, {"max_length": 10})]}

            summary: str

        article = Article(summary="This is a very long summary that needs truncation")
        assert article.summary == "This is a "
        assert len(article.summary) == 10


class TestConfigBasedValidators:
    """Test Config-based validator functionality."""

    def test_simple_validator(self):
        """Test single field validator."""

        class User(PydanticModel):
            class Config:
                apply_validators = {("age",): lambda x: 0 <= x <= 120}

            age: int

        # Valid age
        user = User(age=25)
        assert user.age == 25

        # Invalid age - too high
        with pytest.raises(ValidationError):
            User(age=150)

        # Invalid age - negative
        with pytest.raises(ValidationError):
            User(age=-5)

    def test_multiple_validators_same_field(self):
        """Test multiple validators on same field."""

        def not_empty(s: str) -> bool:
            return len(s.strip()) > 0

        def max_length(s: str) -> bool:
            return len(s) <= 50

        class User(PydanticModel):
            class Config:
                apply_validators = {("username",): [not_empty, max_length]}

            username: str

        # Valid username
        user = User(username="admin")
        assert user.username == "admin"

        # Empty username
        with pytest.raises(ValidationError):
            User(username="   ")

        # Too long username
        with pytest.raises(ValidationError):
            User(username="x" * 51)

    def test_validator_with_args(self):
        """Test validator with additional arguments."""

        def min_length(text: str, min_len: int) -> bool:
            return len(text) >= min_len

        class User(PydanticModel):
            class Config:
                apply_validators = {("password",): [(min_length, {"min_len": 8})]}

            password: str

        # Valid password
        user = User(password="secret123")
        assert user.password == "secret123"

        # Too short
        with pytest.raises(ValidationError):
            User(password="short")


class TestGlobalValidators:
    """Test global validator functionality."""

    def test_global_cross_field_validation(self):
        """Test global validator with cross-field logic."""

        class User(PydanticModel):
            class Config:
                global_validators = [lambda v: v["age"] >= 18 or v["role"] != "admin"]

            age: int
            role: str

        # Valid: adult admin
        user = User(age=25, role="admin")
        assert user.age == 25
        assert user.role == "admin"

        # Valid: minor user
        user = User(age=16, role="user")
        assert user.age == 16
        assert user.role == "user"

        # Invalid: minor admin
        with pytest.raises(ValidationError):
            User(age=16, role="admin")

    def test_multiple_global_validators(self):
        """Test multiple global validators."""

        class User(PydanticModel):
            class Config:
                global_validators = [
                    lambda v: v["age"] >= 18 or v["role"] != "admin",
                    lambda v: v["email"].endswith("@company.com") or v["role"] != "admin",
                ]

            email: str
            age: int
            role: str

        # Valid: adult admin with company email
        user = User(email="admin@company.com", age=25, role="admin")
        assert user.email == "admin@company.com"

        # Invalid: adult admin with non-company email
        with pytest.raises(ValidationError):
            User(email="admin@gmail.com", age=25, role="admin")

        # Valid: regular user with any email
        user = User(email="user@gmail.com", age=25, role="user")
        assert user.email == "user@gmail.com"


class TestAutoInjection:
    """Test auto-injection of field values."""

    def test_auto_inject_field_values(self):
        """Test validators can reference other fields by name."""

        def validate_password_match(password: str, confirm_password: str) -> bool:
            return password == confirm_password

        class User(PydanticModel):
            class Config:
                apply_validators = {("password",): validate_password_match}

            password: str
            confirm_password: str

        # Matching passwords
        user = User(password="secret123", confirm_password="secret123")
        assert user.password == "secret123"

        # Non-matching passwords
        with pytest.raises(ValidationError):
            User(password="secret123", confirm_password="different")

    def test_all_values_parameter(self):
        """Test validators can use all_values parameter."""

        def validate_email_domain(email: str, all_values: dict) -> bool:
            if all_values.get("role") == "admin":
                return email.endswith("@company.com")
            return True

        class User(PydanticModel):
            class Config:
                apply_validators = {("email",): validate_email_domain}

            email: str
            role: str

        # Admin with company email
        user = User(email="admin@company.com", role="admin")
        assert user.email == "admin@company.com"

        # Regular user with any email
        user = User(email="user@gmail.com", role="user")
        assert user.email == "user@gmail.com"

        # Admin with non-company email
        with pytest.raises(ValidationError):
            User(email="admin@gmail.com", role="admin")


class TestSerialization:
    """Test serialization methods."""

    def test_to_dict(self):
        """Test to_dict method."""

        class User(PydanticModel):
            email: str
            age: int
            role: str = "user"

        user = User(email="admin@example.com", age=25)
        data = user.to_dict()

        assert data == {"email": "admin@example.com", "age": 25, "role": "user"}

    def test_to_dict_exclude_none(self):
        """Test to_dict with exclude_none."""

        class User(PydanticModel):
            email: str
            age: int
            role: str | None = None

        user = User(email="admin@example.com", age=25)
        data = user.to_dict(exclude_none=True)

        assert data == {"email": "admin@example.com", "age": 25}
        assert "role" not in data

    def test_to_dict_exclude_fields(self):
        """Test to_dict with exclude_fields."""

        class User(PydanticModel):
            email: str
            age: int
            role: str = "user"

        user = User(email="admin@example.com", age=25)
        data = user.to_dict(exclude_fields=["role"])

        assert data == {"email": "admin@example.com", "age": 25}
        assert "role" not in data

    def test_from_dict(self):
        """Test from_dict method."""

        class User(PydanticModel):
            email: str
            age: int

        user = User.from_dict({"email": "admin@example.com", "age": 25})

        assert user.email == "admin@example.com"
        assert user.age == 25

    def test_json_serialization(self):
        """Test JSON serialization."""

        class User(PydanticModel):
            email: str
            age: int

        user = User(email="admin@example.com", age=25)
        json_str = user.json()

        assert "admin@example.com" in json_str
        assert "25" in json_str

    def test_model_validate_json(self):
        """Test model_validate_json method."""

        class User(PydanticModel):
            email: str
            age: int

        user = User.model_validate_json('{"email": "admin@example.com", "age": 25}')

        assert user.email == "admin@example.com"
        assert user.age == 25


class TestPydanticCompatibility:
    """Test compatibility with Pydantic features."""

    def test_pydantic_field(self):
        """Test using Pydantic Field."""
        from pydantic import Field

        class User(PydanticModel):
            email: str = Field(description="User email")
            age: int = Field(ge=0, le=120)
            name: str = Field(alias="full_name")

        user = User(full_name="John Doe", email="john@example.com", age=25)
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.age == 25

    def test_computed_field(self):
        """Test computed fields."""
        from pydantic import computed_field

        class User(PydanticModel):
            first_name: str
            last_name: str

            @computed_field
            @property
            def full_name(self) -> str:
                return f"{self.first_name} {self.last_name}"

        user = User(first_name="John", last_name="Doe")
        assert user.full_name == "John Doe"

    def test_default_values(self):
        """Test default values."""

        class User(PydanticModel):
            email: str
            age: int
            role: str = "user"
            active: bool = True

        user = User(email="admin@example.com", age=25)
        assert user.role == "user"
        assert user.active is True

    def test_optional_fields(self):
        """Test optional fields."""

        class User(PydanticModel):
            email: str
            age: int
            middle_name: str | None = None

        user = User(email="admin@example.com", age=25)
        assert user.middle_name is None

        user = User(email="admin@example.com", age=25, middle_name="James")
        assert user.middle_name == "James"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
