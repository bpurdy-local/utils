"""Tests for Pydantic Validator utility class."""

from typing import Annotated

import pytest
from pydantic import AfterValidator, BaseModel, ValidationError

from utils.pydantic import Validator


class TestEmail:
    """Tests for Validator.email()"""

    def test_email_valid(self):
        """Test email validator with valid email."""

        class User(BaseModel):
            email: Annotated[str, AfterValidator(Validator.email())]

        user = User(email="test@example.com")
        assert user.email == "test@example.com"

    def test_email_invalid(self):
        """Test email validator with invalid email."""

        class User(BaseModel):
            email: Annotated[str, AfterValidator(Validator.email())]

        with pytest.raises(ValidationError) as exc_info:
            User(email="invalid-email")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "Invalid email format" in str(errors[0]["ctx"]["error"])

    def test_email_custom_error_message(self):
        """Test email validator with custom error message."""

        class User(BaseModel):
            email: Annotated[str, AfterValidator(Validator.email(error_message="Bad email!"))]

        with pytest.raises(ValidationError) as exc_info:
            User(email="not-an-email")

        errors = exc_info.value.errors()
        assert "Bad email!" in str(errors[0]["ctx"]["error"])


class TestUrl:
    """Tests for Validator.url()"""

    def test_url_valid(self):
        """Test URL validator with valid URL."""

        class Resource(BaseModel):
            url: Annotated[str, AfterValidator(Validator.url())]

        resource = Resource(url="https://example.com")
        assert resource.url == "https://example.com"

    def test_url_http_valid(self):
        """Test URL validator with http URL."""

        class Resource(BaseModel):
            url: Annotated[str, AfterValidator(Validator.url())]

        resource = Resource(url="http://example.com/path")
        assert resource.url == "http://example.com/path"

    def test_url_invalid(self):
        """Test URL validator with invalid URL."""

        class Resource(BaseModel):
            url: Annotated[str, AfterValidator(Validator.url())]

        with pytest.raises(ValidationError) as exc_info:
            Resource(url="not-a-url")

        errors = exc_info.value.errors()
        assert "Invalid URL format" in str(errors[0]["ctx"]["error"])


class TestPhone:
    """Tests for Validator.phone()"""

    def test_phone_valid(self):
        """Test phone validator with valid phone."""

        class Contact(BaseModel):
            phone: Annotated[str, AfterValidator(Validator.phone())]

        contact = Contact(phone="555-123-4567")
        assert contact.phone == "555-123-4567"

    def test_phone_valid_with_formatting(self):
        """Test phone validator with various formats."""

        class Contact(BaseModel):
            phone: Annotated[str, AfterValidator(Validator.phone())]

        Contact(phone="(555) 123-4567")
        Contact(phone="+1-555-123-4567")
        Contact(phone="5551234567")

    def test_phone_too_short(self):
        """Test phone validator with too few digits."""

        class Contact(BaseModel):
            phone: Annotated[str, AfterValidator(Validator.phone())]

        with pytest.raises(ValidationError) as exc_info:
            Contact(phone="123")

        errors = exc_info.value.errors()
        assert "Invalid phone number" in str(errors[0]["ctx"]["error"])


class TestMinLength:
    """Tests for Validator.min_length()"""

    def test_min_length_valid(self):
        """Test min_length validator with valid string."""

        class User(BaseModel):
            username: Annotated[str, AfterValidator(Validator.min_length(length=3))]

        user = User(username="john")
        assert user.username == "john"

    def test_min_length_exact(self):
        """Test min_length validator with exact length."""

        class User(BaseModel):
            username: Annotated[str, AfterValidator(Validator.min_length(length=4))]

        user = User(username="john")
        assert user.username == "john"

    def test_min_length_too_short(self):
        """Test min_length validator with too short string."""

        class User(BaseModel):
            username: Annotated[str, AfterValidator(Validator.min_length(length=5))]

        with pytest.raises(ValidationError) as exc_info:
            User(username="bob")

        errors = exc_info.value.errors()
        assert "at least 5 characters" in str(errors[0]["ctx"]["error"])


class TestMaxLength:
    """Tests for Validator.max_length()"""

    def test_max_length_valid(self):
        """Test max_length validator with valid string."""

        class User(BaseModel):
            bio: Annotated[str, AfterValidator(Validator.max_length(length=100))]

        user = User(bio="Short bio")
        assert user.bio == "Short bio"

    def test_max_length_exact(self):
        """Test max_length validator with exact length."""

        class User(BaseModel):
            code: Annotated[str, AfterValidator(Validator.max_length(length=5))]

        user = User(code="12345")
        assert user.code == "12345"

    def test_max_length_too_long(self):
        """Test max_length validator with too long string."""

        class User(BaseModel):
            bio: Annotated[str, AfterValidator(Validator.max_length(length=10))]

        with pytest.raises(ValidationError) as exc_info:
            User(bio="This is a very long bio that exceeds the limit")

        errors = exc_info.value.errors()
        assert "at most 10 characters" in str(errors[0]["ctx"]["error"])


class TestLengthRange:
    """Tests for Validator.length_range()"""

    def test_length_range_valid(self):
        """Test length_range validator with valid string."""

        class User(BaseModel):
            password: Annotated[
                str, AfterValidator(Validator.length_range(min_length=8, max_length=128))
            ]

        user = User(password="MyPass123!")
        assert user.password == "MyPass123!"

    def test_length_range_at_min(self):
        """Test length_range validator at minimum."""

        class User(BaseModel):
            password: Annotated[
                str, AfterValidator(Validator.length_range(min_length=8, max_length=20))
            ]

        user = User(password="12345678")
        assert user.password == "12345678"

    def test_length_range_at_max(self):
        """Test length_range validator at maximum."""

        class User(BaseModel):
            password: Annotated[
                str, AfterValidator(Validator.length_range(min_length=5, max_length=10))
            ]

        user = User(password="1234567890")
        assert user.password == "1234567890"

    def test_length_range_too_short(self):
        """Test length_range validator with too short string."""

        class User(BaseModel):
            password: Annotated[
                str, AfterValidator(Validator.length_range(min_length=8, max_length=20))
            ]

        with pytest.raises(ValidationError) as exc_info:
            User(password="short")

        errors = exc_info.value.errors()
        assert "between 8 and 20 characters" in str(errors[0]["ctx"]["error"])

    def test_length_range_too_long(self):
        """Test length_range validator with too long string."""

        class User(BaseModel):
            password: Annotated[
                str, AfterValidator(Validator.length_range(min_length=8, max_length=16))
            ]

        with pytest.raises(ValidationError) as exc_info:
            User(password="this_is_way_too_long_password")

        errors = exc_info.value.errors()
        assert "between 8 and 16 characters" in str(errors[0]["ctx"]["error"])


class TestRegexPattern:
    """Tests for Validator.regex_pattern()"""

    def test_regex_pattern_valid(self):
        """Test regex_pattern validator with valid input."""

        class User(BaseModel):
            username: Annotated[
                str, AfterValidator(Validator.regex_pattern(pattern=r"^[a-zA-Z0-9_]+$"))
            ]

        user = User(username="john_doe123")
        assert user.username == "john_doe123"

    def test_regex_pattern_invalid(self):
        """Test regex_pattern validator with invalid input."""

        class User(BaseModel):
            username: Annotated[
                str, AfterValidator(Validator.regex_pattern(pattern=r"^[a-zA-Z0-9_]+$"))
            ]

        with pytest.raises(ValidationError) as exc_info:
            User(username="john-doe!")

        errors = exc_info.value.errors()
        assert "must match pattern" in str(errors[0]["ctx"]["error"])


class TestChoices:
    """Tests for Validator.choices()"""

    def test_choices_valid(self):
        """Test choices validator with valid choice."""

        class User(BaseModel):
            role: Annotated[str, AfterValidator(Validator.choices(options=["admin", "user", "guest"]))]

        user = User(role="admin")
        assert user.role == "admin"

    def test_choices_invalid(self):
        """Test choices validator with invalid choice."""

        class User(BaseModel):
            role: Annotated[str, AfterValidator(Validator.choices(options=["admin", "user"]))]

        with pytest.raises(ValidationError) as exc_info:
            User(role="superuser")

        errors = exc_info.value.errors()
        assert "must be one of" in str(errors[0]["ctx"]["error"])

    def test_choices_numeric(self):
        """Test choices validator with numeric choices."""

        class Config(BaseModel):
            level: Annotated[int, AfterValidator(Validator.choices(options=[1, 2, 3]))]

        config = Config(level=2)
        assert config.level == 2


class TestNumericRange:
    """Tests for Validator.numeric_range()"""

    def test_numeric_range_valid(self):
        """Test numeric_range validator with valid value."""

        class Product(BaseModel):
            price: Annotated[
                float, AfterValidator(Validator.numeric_range(min_value=0.0, max_value=10000.0))
            ]

        product = Product(price=99.99)
        assert product.price == 99.99

    def test_numeric_range_at_min(self):
        """Test numeric_range validator at minimum."""

        class Product(BaseModel):
            price: Annotated[
                float, AfterValidator(Validator.numeric_range(min_value=0.0, max_value=100.0))
            ]

        product = Product(price=0.0)
        assert product.price == 0.0

    def test_numeric_range_at_max(self):
        """Test numeric_range validator at maximum."""

        class Product(BaseModel):
            price: Annotated[
                float, AfterValidator(Validator.numeric_range(min_value=0.0, max_value=100.0))
            ]

        product = Product(price=100.0)
        assert product.price == 100.0

    def test_numeric_range_below_min(self):
        """Test numeric_range validator below minimum."""

        class Product(BaseModel):
            price: Annotated[
                float, AfterValidator(Validator.numeric_range(min_value=0.0, max_value=100.0))
            ]

        with pytest.raises(ValidationError) as exc_info:
            Product(price=-10.0)

        errors = exc_info.value.errors()
        assert "between 0.0 and 100.0" in str(errors[0]["ctx"]["error"])

    def test_numeric_range_above_max(self):
        """Test numeric_range validator above maximum."""

        class Product(BaseModel):
            price: Annotated[
                float, AfterValidator(Validator.numeric_range(min_value=0.0, max_value=100.0))
            ]

        with pytest.raises(ValidationError) as exc_info:
            Product(price=200.0)

        errors = exc_info.value.errors()
        assert "between 0.0 and 100.0" in str(errors[0]["ctx"]["error"])

    def test_numeric_range_min_only(self):
        """Test numeric_range validator with only minimum."""

        class Config(BaseModel):
            age: Annotated[int, AfterValidator(Validator.numeric_range(min_value=0))]

        Config(age=25)
        Config(age=0)

        with pytest.raises(ValidationError):
            Config(age=-1)

    def test_numeric_range_max_only(self):
        """Test numeric_range validator with only maximum."""

        class Config(BaseModel):
            percentage: Annotated[int, AfterValidator(Validator.numeric_range(max_value=100))]

        Config(percentage=50)
        Config(percentage=100)

        with pytest.raises(ValidationError):
            Config(percentage=101)


class TestListMinLength:
    """Tests for Validator.list_min_length()"""

    def test_list_min_length_valid(self):
        """Test list_min_length validator with valid list."""

        class Team(BaseModel):
            members: Annotated[list[str], AfterValidator(Validator.list_min_length(length=1))]

        team = Team(members=["Alice", "Bob"])
        assert len(team.members) == 2

    def test_list_min_length_exact(self):
        """Test list_min_length validator with exact length."""

        class Team(BaseModel):
            members: Annotated[list[str], AfterValidator(Validator.list_min_length(length=2))]

        team = Team(members=["Alice", "Bob"])
        assert len(team.members) == 2

    def test_list_min_length_too_short(self):
        """Test list_min_length validator with too few items."""

        class Team(BaseModel):
            members: Annotated[list[str], AfterValidator(Validator.list_min_length(length=3))]

        with pytest.raises(ValidationError) as exc_info:
            Team(members=["Alice"])

        errors = exc_info.value.errors()
        assert "at least 3 items" in str(errors[0]["ctx"]["error"])


class TestListMaxLength:
    """Tests for Validator.list_max_length()"""

    def test_list_max_length_valid(self):
        """Test list_max_length validator with valid list."""

        class Survey(BaseModel):
            answers: Annotated[list[str], AfterValidator(Validator.list_max_length(length=10))]

        survey = Survey(answers=["A", "B", "C"])
        assert len(survey.answers) == 3

    def test_list_max_length_exact(self):
        """Test list_max_length validator with exact length."""

        class Survey(BaseModel):
            answers: Annotated[list[str], AfterValidator(Validator.list_max_length(length=3))]

        survey = Survey(answers=["A", "B", "C"])
        assert len(survey.answers) == 3

    def test_list_max_length_too_long(self):
        """Test list_max_length validator with too many items."""

        class Survey(BaseModel):
            answers: Annotated[list[str], AfterValidator(Validator.list_max_length(length=2))]

        with pytest.raises(ValidationError) as exc_info:
            Survey(answers=["A", "B", "C", "D"])

        errors = exc_info.value.errors()
        assert "at most 2 items" in str(errors[0]["ctx"]["error"])


class TestNotEmpty:
    """Tests for Validator.not_empty()"""

    def test_not_empty_valid_string(self):
        """Test not_empty validator with non-empty string."""

        class User(BaseModel):
            name: Annotated[str, AfterValidator(Validator.not_empty())]

        user = User(name="John")
        assert user.name == "John"

    def test_not_empty_whitespace_only(self):
        """Test not_empty validator with whitespace-only string."""

        class User(BaseModel):
            name: Annotated[str, AfterValidator(Validator.not_empty())]

        with pytest.raises(ValidationError) as exc_info:
            User(name="   ")

        errors = exc_info.value.errors()
        assert "cannot be empty" in str(errors[0]["ctx"]["error"])

    def test_not_empty_empty_string(self):
        """Test not_empty validator with empty string."""

        class User(BaseModel):
            name: Annotated[str, AfterValidator(Validator.not_empty())]

        with pytest.raises(ValidationError) as exc_info:
            User(name="")

        errors = exc_info.value.errors()
        assert "cannot be empty" in str(errors[0]["ctx"]["error"])

    def test_not_empty_valid_list(self):
        """Test not_empty validator with non-empty list."""

        class Team(BaseModel):
            members: Annotated[list[str], AfterValidator(Validator.not_empty())]

        team = Team(members=["Alice"])
        assert len(team.members) == 1

    def test_not_empty_empty_list(self):
        """Test not_empty validator with empty list."""

        class Team(BaseModel):
            members: Annotated[list[str], AfterValidator(Validator.not_empty())]

        with pytest.raises(ValidationError) as exc_info:
            Team(members=[])

        errors = exc_info.value.errors()
        assert "cannot be empty" in str(errors[0]["ctx"]["error"])


class TestCombinedValidators:
    """Tests for combining multiple validators."""

    def test_multiple_validators(self):
        """Test field with multiple validators."""

        class User(BaseModel):
            username: Annotated[
                str,
                AfterValidator(Validator.min_length(length=3)),
                AfterValidator(Validator.max_length(length=20)),
                AfterValidator(Validator.regex_pattern(pattern=r"^[a-zA-Z0-9_]+$")),
            ]

        user = User(username="john_doe")
        assert user.username == "john_doe"

        # Test too short
        with pytest.raises(ValidationError):
            User(username="ab")

        # Test too long
        with pytest.raises(ValidationError):
            User(username="a" * 30)

        # Test invalid pattern
        with pytest.raises(ValidationError):
            User(username="john-doe!")
