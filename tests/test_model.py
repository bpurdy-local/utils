"""Tests for Model system."""

import pytest

from utils.model import (
    BoolField,
    Field,
    FloatField,
    IntField,
    Model,
    StringField,
    ValidationError,
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
    return text[:length]


def is_email(text: str) -> bool:
    """Simple email validator."""
    return "@" in text and "." in text


def in_range(value: int, *, min: int, max: int) -> bool:
    """Check if value is in range."""
    return min <= value <= max


def clamp(value: int, *, min: int, max: int) -> int:
    """Clamp value to range."""
    if value < min:
        return min
    if value > max:
        return max
    return value


class TestBasicFields:
    """Test basic field functionality."""

    def test_string_field_basic(self):
        """Test basic StringField."""

        class User(Model):
            name: StringField = StringField()

        user = User(name="Alice")
        assert user.name == "Alice"

    def test_int_field_basic(self):
        """Test basic IntField."""

        class User(Model):
            age: IntField = IntField()

        user = User(age=25)
        assert user.age == 25

    def test_float_field_basic(self):
        """Test basic FloatField."""

        class User(Model):
            score: FloatField = FloatField()

        user = User(score=95.5)
        assert user.score == 95.5

    def test_bool_field_basic(self):
        """Test basic BoolField."""

        class User(Model):
            active: BoolField = BoolField()

        user = User(active=True)
        assert user.active is True

    def test_multiple_fields(self):
        """Test model with multiple fields."""

        class User(Model):
            name: StringField = StringField()
            age: IntField = IntField()
            score: FloatField = FloatField()

        user = User(name="Alice", age=25, score=95.5)
        assert user.name == "Alice"
        assert user.age == 25
        assert user.score == 95.5


class TestTransforms:
    """Test field transformations."""

    def test_single_transform(self):
        """Test single transform function."""

        class User(Model):
            name: StringField = StringField(transform=strip)

        user = User(name="  Alice  ")
        assert user.name == "Alice"

    def test_multiple_transforms(self):
        """Test multiple transforms in sequence."""

        class User(Model):
            email: StringField = StringField(transform=[strip, lower])

        user = User(email="  ADMIN@EXAMPLE.COM  ")
        assert user.email == "admin@example.com"

    def test_transform_with_args_tuple(self):
        """Test transform with arguments using tuple syntax."""

        class User(Model):
            name: StringField = StringField(transform=[(truncate, {"length": 5})])

        user = User(name="Alexander")
        assert user.name == "Alexa"

    def test_mixed_transforms(self):
        """Test mix of simple and tuple transforms."""

        class User(Model):
            email: StringField = StringField(transform=[strip, lower, (truncate, {"length": 10})])

        user = User(email="  ADMIN@EXAMPLE.COM  ")
        assert user.email == "admin@exam"

    def test_transform_on_assignment(self):
        """Test that transforms run on field assignment."""

        class User(Model):
            email: StringField = StringField(transform=[strip, lower])

        user = User(email="admin@example.com")
        user.email = "  NEW@EXAMPLE.COM  "
        assert user.email == "new@example.com"


class TestValidation:
    """Test field validation."""

    def test_simple_validator(self):
        """Test simple validator function."""

        class User(Model):
            email: StringField = StringField(validate=is_email)

        user = User(email="admin@example.com")
        assert user.email == "admin@example.com"

    def test_validator_fails(self):
        """Test validator failure raises ValidationError."""

        class User(Model):
            email: StringField = StringField(validate=is_email)

        with pytest.raises(ValidationError, match="Validation failed"):
            User(email="not-an-email")

    def test_validator_with_args(self):
        """Test validator with arguments using tuple syntax."""

        class User(Model):
            age: IntField = IntField(validate=(in_range, {"min": 0, "max": 120}))

        user = User(age=25)
        assert user.age == 25

    def test_validator_with_args_fails(self):
        """Test validator with args failure."""

        class User(Model):
            age: IntField = IntField(validate=(in_range, {"min": 0, "max": 120}))

        with pytest.raises(ValidationError):
            User(age=150)

    def test_validation_on_assignment(self):
        """Test that validation runs on field assignment."""

        class User(Model):
            email: StringField = StringField(validate=is_email)

        user = User(email="admin@example.com")

        with pytest.raises(ValidationError):
            user.email = "invalid"

    def test_transform_before_validate(self):
        """Test that transforms run before validation."""

        class User(Model):
            email: StringField = StringField(transform=[strip, lower], validate=is_email)

        # Validator should see transformed value
        user = User(email="  ADMIN@EXAMPLE.COM  ")
        assert user.email == "admin@example.com"


class TestTypeCoercion:
    """Test automatic type coercion for fields."""

    def test_string_field_converts_int(self):
        """Test StringField auto-converts int to string."""

        class User(Model):
            name: StringField = StringField()

        user = User(name=123)
        assert user.name == "123"
        assert isinstance(user.name, str)

    def test_string_field_converts_float(self):
        """Test StringField auto-converts float to string."""

        class User(Model):
            name: StringField = StringField()

        user = User(name=3.14)
        assert user.name == "3.14"
        assert isinstance(user.name, str)

    def test_int_field_converts_string(self):
        """Test IntField auto-converts string to int."""

        class User(Model):
            age: IntField = IntField()

        user = User(age="25")
        assert user.age == 25
        assert isinstance(user.age, int)

    def test_int_field_converts_float(self):
        """Test IntField auto-converts float to int."""

        class User(Model):
            age: IntField = IntField()

        user = User(age=25.7)
        assert user.age == 25
        assert isinstance(user.age, int)

    def test_int_field_invalid_conversion(self):
        """Test IntField fails on invalid conversion."""

        class User(Model):
            age: IntField = IntField()

        with pytest.raises(ValidationError, match="cannot convert"):
            User(age="not a number")

    def test_float_field_converts_int(self):
        """Test FloatField converts int to float."""

        class User(Model):
            score: FloatField = FloatField()

        user = User(score=95)
        assert user.score == 95.0
        assert isinstance(user.score, float)

    def test_float_field_converts_string(self):
        """Test FloatField auto-converts string to float."""

        class User(Model):
            score: FloatField = FloatField()

        user = User(score="95.5")
        assert user.score == 95.5
        assert isinstance(user.score, float)

    def test_float_field_invalid_conversion(self):
        """Test FloatField fails on invalid conversion."""

        class User(Model):
            score: FloatField = FloatField()

        with pytest.raises(ValidationError, match="cannot convert"):
            User(score="not a number")

    def test_bool_field_converts_int(self):
        """Test BoolField auto-converts int to bool."""

        class User(Model):
            active: BoolField = BoolField()

        user1 = User(active=1)
        assert user1.active is True

        user2 = User(active=0)
        assert user2.active is False

    def test_bool_field_converts_string(self):
        """Test BoolField auto-converts string to bool."""

        class User(Model):
            active: BoolField = BoolField()

        # True values
        for val in ["true", "True", "TRUE", "1", "yes", "Yes", "on", "ON"]:
            user = User(active=val)
            assert user.active is True, f"Failed for {val!r}"

        # False values
        for val in ["false", "False", "FALSE", "0", "no", "No", "off", "OFF"]:
            user = User(active=val)
            assert user.active is False, f"Failed for {val!r}"

    def test_bool_field_invalid_string_conversion(self):
        """Test BoolField fails on invalid string."""

        class User(Model):
            active: BoolField = BoolField()

        with pytest.raises(ValidationError, match="cannot convert string"):
            User(active="maybe")


class TestOptionalFields:
    """Test optional field support."""

    def test_optional_field_with_none(self):
        """Test optional field can be None."""

        class User(Model):
            name: StringField = StringField()
            nickname: StringField | None = None

        user = User(name="Alice")
        assert user.name == "Alice"
        assert user.nickname is None

    def test_optional_field_with_value(self):
        """Test optional field can have value."""

        class User(Model):
            name: StringField = StringField()
            nickname: StringField | None = None

        user = User(name="Alice", nickname="Ali")
        assert user.nickname == "Ali"

    def test_optional_field_set_to_none(self):
        """Test optional field can be set to None."""

        class User(Model):
            nickname: StringField | None = None

        user = User(nickname="Ali")
        user.nickname = None
        assert user.nickname is None


class TestDefaults:
    """Test default values."""

    def test_field_with_default(self):
        """Test field with default value."""

        class User(Model):
            name: StringField = StringField()
            role: StringField = StringField(default="user")

        user = User(name="Alice")
        assert user.role == "user"

    def test_field_override_default(self):
        """Test overriding default value."""

        class User(Model):
            name: StringField = StringField()
            role: StringField = StringField(default="user")

        user = User(name="Alice", role="admin")
        assert user.role == "admin"

    def test_default_with_transform(self):
        """Test default value goes through transforms."""

        class User(Model):
            role: StringField = StringField(default="USER", transform=[lower])

        user = User()
        assert user.role == "user"


class TestRequiredFields:
    """Test required field validation."""

    def test_required_field_missing(self):
        """Test missing required field raises error."""

        class User(Model):
            name: StringField = StringField()
            age: IntField = IntField()

        with pytest.raises(ValidationError, match="Required field 'age' is missing"):
            User(name="Alice")

    def test_all_required_fields_present(self):
        """Test all required fields present."""

        class User(Model):
            name: StringField = StringField()
            age: IntField = IntField()

        user = User(name="Alice", age=25)
        assert user.name == "Alice"
        assert user.age == 25


class TestDictConversion:
    """Test dict conversion methods."""

    def test_to_dict(self):
        """Test to_dict method."""

        class User(Model):
            name: StringField = StringField()
            age: IntField = IntField()

        user = User(name="Alice", age=25)
        data = user.to_dict()

        assert data == {"name": "Alice", "age": 25}

    def test_model_dump(self):
        """Test model_dump (Pydantic alias)."""

        class User(Model):
            name: StringField = StringField()
            age: IntField = IntField()

        user = User(name="Alice", age=25)
        data = user.model_dump()

        assert data == {"name": "Alice", "age": 25}

    def test_from_dict(self):
        """Test from_dict method."""

        class User(Model):
            name: StringField = StringField()
            age: IntField = IntField()

        user = User.from_dict({"name": "Alice", "age": 25})

        assert user.name == "Alice"
        assert user.age == 25

    def test_model_validate(self):
        """Test model_validate (Pydantic alias)."""

        class User(Model):
            name: StringField = StringField()
            age: IntField = IntField()

        user = User.model_validate({"name": "Alice", "age": 25})

        assert user.name == "Alice"
        assert user.age == 25

    def test_dict_round_trip(self):
        """Test converting to dict and back."""

        class User(Model):
            name: StringField = StringField()
            age: IntField = IntField()
            active: BoolField = BoolField()

        user1 = User(name="Alice", age=25, active=True)
        data = user1.to_dict()
        user2 = User.from_dict(data)

        assert user1 == user2

    def test_dict_with_optional_fields(self):
        """Test dict conversion with optional fields."""

        class User(Model):
            name: StringField = StringField()
            nickname: StringField | None = None

        user = User(name="Alice")
        data = user.to_dict()

        assert data == {"name": "Alice", "nickname": None}


class TestModelMethods:
    """Test model helper methods."""

    def test_repr(self):
        """Test __repr__ method."""

        class User(Model):
            name: StringField = StringField()
            age: IntField = IntField()

        user = User(name="Alice", age=25)
        repr_str = repr(user)

        assert "User" in repr_str
        assert "name='Alice'" in repr_str
        assert "age=25" in repr_str

    def test_equality(self):
        """Test __eq__ method."""

        class User(Model):
            name: StringField = StringField()
            age: IntField = IntField()

        user1 = User(name="Alice", age=25)
        user2 = User(name="Alice", age=25)
        user3 = User(name="Bob", age=30)

        assert user1 == user2
        assert user1 != user3

    def test_equality_different_type(self):
        """Test equality with different type."""

        class User(Model):
            name: StringField = StringField()

        user = User(name="Alice")
        assert user != "Alice"
        assert user != {"name": "Alice"}


class TestComplexExample:
    """Test complex real-world example."""

    def test_user_model(self):
        """Test comprehensive user model."""

        class User(Model):
            email: StringField = StringField(transform=[strip, lower], validate=is_email)
            age: IntField = IntField(validate=(in_range, {"min": 0, "max": 120}))
            name: StringField | None = None
            role: StringField = StringField(default="user")

        # Create user with transforms and validation
        user = User(email="  ADMIN@EXAMPLE.COM  ", age=25, name="Alice")

        assert user.email == "admin@example.com"
        assert user.age == 25
        assert user.name == "Alice"
        assert user.role == "user"

        # Update fields with re-validation
        user.age = 30
        assert user.age == 30

        with pytest.raises(ValidationError):
            user.age = 150

        # Dict conversion
        data = user.to_dict()
        user2 = User.from_dict(data)
        assert user == user2

    def test_transform_returns_value(self):
        """Test transform that returns modified value."""

        class User(Model):
            age: IntField = IntField(transform=[(clamp, {"min": 0, "max": 120})])

        user = User(age=150)
        assert user.age == 120  # Clamped to max

        user = User(age=-10)
        assert user.age == 0  # Clamped to min


class TestBulkTransformsValidators:
    """Test bulk application of transforms and validators."""

    def test_apply_transforms_to_multiple_fields(self):
        """Test applying transforms to multiple fields at once."""

        class User(Model):
            class Config:
                apply_transforms = {
                    ("email", "username"): [strip, lower],
                }

            email: StringField = StringField()
            username: StringField = StringField()
            bio: StringField = StringField()

        user = User(email="  ADMIN@EXAMPLE.COM  ", username="  ADMIN  ", bio="Hello")
        assert user.email == "admin@example.com"
        assert user.username == "admin"
        assert user.bio == "Hello"  # Not affected

    def test_apply_validators_to_multiple_fields(self):
        """Test applying validators to multiple fields at once."""

        def not_empty(text: str) -> bool:
            return len(text.strip()) > 0

        class User(Model):
            class Config:
                apply_validators = {
                    ("email", "username"): not_empty,
                }

            email: StringField = StringField()
            username: StringField = StringField()
            bio: StringField | None = None

        # Valid
        user = User(email="admin@example.com", username="admin")
        assert user.email == "admin@example.com"

        # Invalid - empty email
        with pytest.raises(ValidationError):
            User(email="   ", username="admin")

        # Invalid - empty username
        with pytest.raises(ValidationError):
            User(email="admin@example.com", username="")

    def test_bulk_transforms_with_existing_transforms(self):
        """Test bulk transforms combine with existing field transforms."""

        class User(Model):
            class Config:
                apply_transforms = {
                    ("email", "username"): [strip, lower],
                }

            email: StringField = StringField(transform=[(truncate, {"length": 10})])
            username: StringField = StringField()

        # Bulk transforms run first, then field-specific transforms
        user = User(email="  ADMIN@EXAMPLE.COM  ", username="  ADMIN  ")
        assert user.email == "admin@exam"  # stripped, lowered, then truncated
        assert user.username == "admin"  # stripped and lowered

    def test_bulk_validators_with_existing_validators(self):
        """Test bulk validators combine with existing field validators."""

        def not_empty(text: str) -> bool:
            return len(text.strip()) > 0

        class User(Model):
            class Config:
                apply_validators = {
                    ("email", "username"): not_empty,
                }

            email: StringField = StringField(validate=is_email)
            username: StringField = StringField()

        # Both validators must pass
        user = User(email="admin@example.com", username="admin")
        assert user.email == "admin@example.com"

        # Fails bulk validator (empty)
        with pytest.raises(ValidationError):
            User(email="", username="admin")

        # Fails field validator (not email)
        with pytest.raises(ValidationError):
            User(email="not-an-email", username="admin")

    def test_multiple_bulk_transform_groups(self):
        """Test multiple bulk transform groups."""

        class User(Model):
            class Config:
                apply_transforms = {
                    ("email", "username"): [strip, lower],
                    ("bio",): [strip],
                }

            email: StringField = StringField()
            username: StringField = StringField()
            bio: StringField = StringField()

        user = User(email="  ADMIN@EXAMPLE.COM  ", username="  ADMIN  ", bio="  Hello World  ")
        assert user.email == "admin@example.com"
        assert user.username == "admin"
        assert user.bio == "Hello World"


class TestGlobalValidators:
    """Test global validators with cross-field logic."""

    def test_global_validator_basic(self):
        """Test basic global validator."""

        def validate_consistency(values: dict) -> bool:
            # Simple validation: email and username should match
            email_prefix = values["email"].split("@")[0]
            return email_prefix == values["username"]

        class User(Model):
            class Config:
                global_validators = [validate_consistency]

            email: StringField = StringField()
            username: StringField = StringField()

        # Valid - email prefix matches username
        user = User(email="admin@example.com", username="admin")
        assert user.email == "admin@example.com"

        # Invalid - email prefix doesn't match username
        with pytest.raises(ValidationError, match="Global validation failed"):
            User(email="admin@example.com", username="user")

    def test_global_validator_cross_field_logic(self):
        """Test global validator with complex cross-field logic."""

        def validate_age_role(values: dict) -> bool:
            if values["age"] < 18 and values["role"] == "admin":
                raise ValidationError("Admins must be 18 or older")
            return True

        class User(Model):
            class Config:
                global_validators = [validate_age_role]

            age: IntField = IntField()
            role: StringField = StringField()

        # Valid - adult admin
        user = User(age=25, role="admin")
        assert user.age == 25

        # Valid - minor user
        user = User(age=16, role="user")
        assert user.age == 16

        # Invalid - minor admin
        with pytest.raises(ValidationError, match="Admins must be 18 or older"):
            User(age=16, role="admin")

    def test_multiple_global_validators(self):
        """Test multiple global validators."""

        def validate_age_role(values: dict) -> bool:
            if values["age"] < 18 and values["role"] == "admin":
                raise ValidationError("Admins must be 18 or older")
            return True

        def validate_email_domain(values: dict) -> bool:
            if values["role"] == "admin" and not values["email"].endswith("@company.com"):
                raise ValidationError("Admins must have company email")
            return True

        class User(Model):
            class Config:
                global_validators = [validate_age_role, validate_email_domain]

            age: IntField = IntField()
            role: StringField = StringField()
            email: StringField = StringField()

        # Valid - meets all criteria
        user = User(age=25, role="admin", email="admin@company.com")
        assert user.role == "admin"

        # Invalid - age check fails
        with pytest.raises(ValidationError, match="Admins must be 18 or older"):
            User(age=16, role="admin", email="admin@company.com")

        # Invalid - email check fails
        with pytest.raises(ValidationError, match="Admins must have company email"):
            User(age=25, role="admin", email="admin@gmail.com")

    def test_global_validator_with_optional_fields(self):
        """Test global validator with optional fields."""

        def validate_bio_length(values: dict) -> bool:
            bio = values.get("bio")
            if bio is not None and len(bio) < 10:
                raise ValidationError("Bio must be at least 10 characters")
            return True

        class User(Model):
            class Config:
                global_validators = [validate_bio_length]

            username: StringField = StringField()
            bio: StringField | None = None

        # Valid - no bio
        user = User(username="admin")
        assert user.bio is None

        # Valid - long bio
        user = User(username="admin", bio="This is a long biography")
        assert user.bio == "This is a long biography"

        # Invalid - short bio
        with pytest.raises(ValidationError, match="Bio must be at least 10 characters"):
            User(username="admin", bio="Short")

    def test_global_validators_run_on_init_only(self):
        """Test that global validators run on init but not on field updates."""

        call_count = {"count": 0}

        def count_calls(values: dict) -> bool:
            call_count["count"] += 1
            return True

        class User(Model):
            class Config:
                global_validators = [count_calls]

            age: IntField = IntField()

        # Global validator runs once on init
        user = User(age=25)
        assert call_count["count"] == 1

        # Global validator does NOT run on field update
        user.age = 30
        assert call_count["count"] == 1  # Still 1, not 2


class TestContextAwareTransformsValidators:
    """Test transforms/validators that use all_values parameter."""

    def test_context_aware_transform(self):
        """Test transform that uses all_values parameter."""

        def prefix_with_username(text: str, *, all_values: dict) -> str:
            """Transform that accesses other field values."""
            username = all_values.get("username", "")
            if username:
                return f"{username}: {text}"
            return text

        class User(Model):
            username: StringField = StringField()
            message: StringField = StringField(transform=[prefix_with_username])

        user = User(username="alice", message="Hello world")
        assert user.message == "alice: Hello world"

    def test_context_aware_validator(self):
        """Test validator that uses all_values parameter."""

        def validate_password_not_username(password: str, *, all_values: dict) -> bool:
            """Validator that checks password doesn't match username."""
            username = all_values.get("username", "")
            if username and password.lower() == username.lower():
                raise ValidationError("Password cannot be the same as username")
            return True

        class User(Model):
            username: StringField = StringField()
            password: StringField = StringField(validate=validate_password_not_username)

        # Valid - different password
        user = User(username="alice", password="secret123")
        assert user.password == "secret123"

        # Invalid - password matches username
        with pytest.raises(ValidationError, match="Password cannot be the same"):
            User(username="alice", password="alice")

    def test_bulk_transform_with_context(self):
        """Test bulk transforms can use all_values."""

        def normalize_email(email: str, *, all_values: dict) -> str:
            """Normalize email based on username."""
            # Always lowercase if username is present
            username = all_values.get("username")
            if username:
                return email.lower()
            return email

        class User(Model):
            class Config:
                apply_transforms = {
                    ("email",): [normalize_email],
                }

            username: StringField = StringField()
            email: StringField = StringField()

        user = User(username="alice", email="ALICE@COMPANY.COM")
        assert user.email == "alice@company.com"

    def test_bulk_validator_with_context(self):
        """Test bulk validators can use all_values."""

        def validate_email_matches_username(email: str, *, all_values: dict) -> bool:
            """Validate email prefix matches username."""
            username = all_values.get("username", "")
            if username and "@" in email:
                email_prefix = email.split("@")[0]
                if email_prefix != username:
                    raise ValidationError("Email must match username")
            return True

        class User(Model):
            class Config:
                apply_validators = {
                    ("email",): validate_email_matches_username,
                }

            username: StringField = StringField()
            email: StringField = StringField()

        # Valid - email matches username
        user = User(username="alice", email="alice@example.com")
        assert user.email == "alice@example.com"

        # Invalid - email doesn't match username
        with pytest.raises(ValidationError, match="Email must match username"):
            User(username="alice", email="bob@example.com")

    def test_mixed_context_and_regular_transforms(self):
        """Test mixing context-aware and regular transforms."""

        def strip(text: str) -> str:
            return text.strip()

        def add_prefix(text: str, *, all_values: dict) -> str:
            role = all_values.get("role", "user")
            return f"[{role}] {text}"

        class User(Model):
            role: StringField = StringField()
            message: StringField = StringField(transform=[strip, add_prefix])

        user = User(role="admin", message="  Hello  ")
        assert user.message == "[admin] Hello"


class TestCustomObjects:
    """Test Model behavior with custom objects."""

    def test_custom_object_storage(self):
        """Test storing custom objects in fields."""

        class CustomObject:
            def __init__(self, value):
                self.value = value

        class MyModel(Model):
            data: Field[CustomObject] = Field()

        obj = CustomObject(42)
        model = MyModel(data=obj)
        assert model.data is obj
        assert model.data.value == 42

    def test_custom_object_with_to_dict(self):
        """Test custom object with to_dict method for JSON serialization."""

        class Address:
            def __init__(self, street, city, zip_code):
                self.street = street
                self.city = city
                self.zip_code = zip_code

            def to_dict(self):
                return {
                    "street": self.street,
                    "city": self.city,
                    "zip_code": self.zip_code,
                }

        class User(Model):
            name: StringField = StringField()
            address: Field[Address] = Field[Address]()

        addr = Address("123 Main St", "Springfield", "12345")
        user = User(name="Alice", address=addr)

        # to_dict includes the custom object
        data = user.to_dict()
        assert data["address"] is addr

        # JSON serialization uses Address.to_dict()
        import json

        json_str = user.json()
        parsed = json.loads(json_str)
        assert parsed["address"]["street"] == "123 Main St"
        assert parsed["address"]["city"] == "Springfield"
        assert parsed["address"]["zip_code"] == "12345"

    def test_custom_object_with_dict_attr(self):
        """Test custom object with __dict__ for JSON serialization."""

        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        class Shape(Model):
            name: StringField = StringField()
            center: Field[Point] = Field[Point]()

        point = Point(10, 20)
        shape = Shape(name="Circle", center=point)

        # JSON uses Point.__dict__
        import json

        json_str = shape.json()
        parsed = json.loads(json_str)
        assert parsed["center"]["x"] == 10
        assert parsed["center"]["y"] == 20

    def test_custom_object_with_validation(self):
        """Test custom objects with validators."""

        class Coordinate:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        def validate_positive_coords(coord: Coordinate) -> bool:
            if coord.x < 0 or coord.y < 0:
                raise ValidationError("Coordinates must be positive")
            return True

        class Location(Model):
            name: StringField = StringField()
            position: Field = Field(validate=validate_positive_coords)

        # Valid coordinates
        loc = Location(name="Home", position=Coordinate(10, 20))
        assert loc.position.x == 10

        # Invalid coordinates
        with pytest.raises(ValidationError, match="Coordinates must be positive"):
            Location(name="Home", position=Coordinate(-5, 10))

    def test_custom_object_with_transform(self):
        """Test custom objects with transforms."""

        class Temperature:
            def __init__(self, celsius):
                self.celsius = celsius

        def normalize_temp(temp: Temperature) -> Temperature:
            """Clamp temperature to reasonable range."""
            temp.celsius = max(-273.15, min(temp.celsius, 1000))
            return temp

        class WeatherData(Model):
            location: StringField = StringField()
            temp: Field = Field(transform=normalize_temp)

        # Transform clamps the temperature
        data = WeatherData(location="Arctic", temp=Temperature(-500))
        assert data.temp.celsius == -273.15

        data = WeatherData(location="Sun", temp=Temperature(5000))
        assert data.temp.celsius == 1000

    def test_datetime_object_json_serialization(self):
        """Test datetime objects are serialized correctly."""
        from datetime import datetime

        class Event(Model):
            name: StringField = StringField()
            timestamp: Field = Field()

        dt = datetime(2024, 1, 15, 10, 30, 0)
        event = Event(name="Meeting", timestamp=dt)

        import json

        json_str = event.json()
        parsed = json.loads(json_str)
        assert parsed["timestamp"] == "2024-01-15T10:30:00"

    def test_date_object_json_serialization(self):
        """Test date objects are serialized correctly."""
        from datetime import date

        class Appointment(Model):
            title: StringField = StringField()
            scheduled_date: Field = Field()

        d = date(2024, 1, 15)
        appt = Appointment(title="Dentist", scheduled_date=d)

        import json

        json_str = appt.json()
        parsed = json.loads(json_str)
        assert parsed["scheduled_date"] == "2024-01-15"

    def test_decimal_object_json_serialization(self):
        """Test Decimal objects are serialized as float."""
        from decimal import Decimal

        class Product(Model):
            name: StringField = StringField()
            price: Field = Field()

        product = Product(name="Widget", price=Decimal("19.99"))

        import json

        json_str = product.json()
        parsed = json.loads(json_str)
        assert parsed["price"] == 19.99
        assert isinstance(parsed["price"], float)

    def test_path_object_json_serialization(self):
        """Test Path objects are serialized as string."""
        from pathlib import Path

        class FileInfo(Model):
            name: StringField = StringField()
            path: Field = Field()

        file_info = FileInfo(name="config", path=Path("/etc/config.yaml"))

        import json

        json_str = file_info.json()
        parsed = json.loads(json_str)
        assert parsed["path"] == "/etc/config.yaml"

    def test_custom_serializer_for_custom_objects(self):
        """Test providing custom serializer for custom types."""

        class Color:
            def __init__(self, r, g, b):
                self.r = r
                self.g = g
                self.b = b

        def serialize_color(obj):
            if isinstance(obj, Color):
                return {
                    "r": obj.r,
                    "g": obj.g,
                    "b": obj.b,
                    "hex": f"#{obj.r:02x}{obj.g:02x}{obj.b:02x}",
                }
            raise TypeError

        class Theme(Model):
            name: StringField = StringField()
            primary_color: Field = Field()

        color = Color(255, 128, 0)
        theme = Theme(name="Sunset", primary_color=color)

        import json

        json_str = theme.json(default=serialize_color)
        parsed = json.loads(json_str)
        assert parsed["primary_color"]["r"] == 255
        assert parsed["primary_color"]["g"] == 128
        assert parsed["primary_color"]["b"] == 0
        assert parsed["primary_color"]["hex"] == "#ff8000"

    def test_custom_serializer_with_fallback_to_default(self):
        """Test custom serializer chains with default serializer."""
        from datetime import datetime
        from decimal import Decimal

        class CustomType:
            def __init__(self, value):
                self.value = value

        def serialize_custom(obj):
            if isinstance(obj, CustomType):
                return {"custom_value": obj.value}
            raise TypeError

        class DataModel(Model):
            custom: Field = Field()
            timestamp: Field = Field()
            price: Field = Field()

        model = DataModel(
            custom=CustomType("test"),
            timestamp=datetime(2024, 1, 15, 10, 30),
            price=Decimal("99.99"),
        )

        import json

        json_str = model.json(default=serialize_custom)
        parsed = json.loads(json_str)

        # Custom serializer handles CustomType
        assert parsed["custom"]["custom_value"] == "test"
        # Default serializer handles datetime
        assert parsed["timestamp"] == "2024-01-15T10:30:00"
        # Default serializer handles Decimal
        assert parsed["price"] == 99.99

    def test_nested_model_json_serialization(self):
        """Test nested Model objects serialize correctly."""

        class Address(Model):
            street: StringField = StringField()
            city: StringField = StringField()

        class Person(Model):
            name: StringField = StringField()
            address: Field = Field()

        addr = Address(street="123 Main St", city="Springfield")
        person = Person(name="Alice", address=addr)

        import json

        json_str = person.json()
        parsed = json.loads(json_str)
        assert parsed["address"]["street"] == "123 Main St"
        assert parsed["address"]["city"] == "Springfield"

    def test_list_of_custom_objects(self):
        """Test storing list of custom objects."""

        class Tag:
            def __init__(self, name, color):
                self.name = name
                self.color = color

            def to_dict(self):
                return {"name": self.name, "color": self.color}

        class Article(Model):
            title: StringField = StringField()
            tags: Field = Field()

        tags = [Tag("python", "blue"), Tag("tutorial", "green")]
        article = Article(title="Python Guide", tags=tags)

        import json

        json_str = article.json()
        parsed = json.loads(json_str)
        assert len(parsed["tags"]) == 2
        assert parsed["tags"][0]["name"] == "python"
        assert parsed["tags"][1]["color"] == "green"

    def test_dict_of_custom_objects(self):
        """Test storing dict of custom objects."""

        class Config:
            def __init__(self, enabled, timeout):
                self.enabled = enabled
                self.timeout = timeout

        class Settings(Model):
            app_name: StringField = StringField()
            modules: Field = Field()

        configs = {
            "auth": Config(True, 30),
            "cache": Config(False, 60),
        }
        settings = Settings(app_name="MyApp", modules=configs)

        import json

        json_str = settings.json()
        parsed = json.loads(json_str)
        assert parsed["modules"]["auth"]["enabled"] is True
        assert parsed["modules"]["auth"]["timeout"] == 30
        assert parsed["modules"]["cache"]["enabled"] is False

    def test_optional_custom_object(self):
        """Test optional fields with custom objects."""

        class Metadata:
            def __init__(self, version):
                self.version = version

        class Document(Model):
            title: StringField = StringField()
            metadata: Metadata | None = None

        # Without metadata
        doc1 = Document(title="Test")
        assert doc1.metadata is None

        # With metadata
        doc2 = Document(title="Test", metadata=Metadata("1.0"))
        assert doc2.metadata.version == "1.0"
