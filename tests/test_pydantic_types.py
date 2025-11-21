"""Tests for Pydantic Field utility class."""

import pytest
from pydantic import BaseModel, ValidationError

from utils import Integer, String
from utils.pydantic import Field, Validator


class TestSingleTransform:
    """Tests for Field.field(transforms=) with single transform function."""

    def test_single_transform_strip(self):
        """Test single transform with lambda x: x.strip()."""

        class User(BaseModel):
            name: Field.field(transforms=lambda x: x.strip())

        user = User(name="  John  ")
        assert user.name == "John"

    def test_single_transform_lower(self):
        """Test single transform with lambda x: x.lower()."""

        class User(BaseModel):
            email: Field.field(transforms=lambda x: x.lower())

        user = User(email="Test@EXAMPLE.COM")
        assert user.email == "test@example.com"

    def test_single_transform_upper(self):
        """Test single transform with lambda x: x.upper()."""

        class Config(BaseModel):
            code: Field.field(transforms=lambda x: x.upper())

        config = Config(code="abc123")
        assert config.code == "ABC123"

    def test_single_transform_slug(self):
        """Test single transform with String.slug."""

        class Article(BaseModel):
            slug: Field.field(transforms=lambda s: String.slug(s))

        article = Article(slug="Hello World!")
        assert article.slug == "hello-world"

    def test_single_transform_truncate(self):
        """Test single transform with String.truncate."""

        class Post(BaseModel):
            summary: Field.field(transforms=lambda s: String.truncate(s, length=10))

        post = Post(summary="This is a very long summary")
        assert post.summary == "This is..."


class TestMultipleTransforms:
    """Tests for Field.field(transforms=) with multiple transform functions."""

    def test_chain_strip_lower(self):
        """Test chaining strip then lower."""

        class User(BaseModel):
            username: Field.field(transforms=[lambda x: x.strip(), lambda x: x.lower()])

        user = User(username="  JohnDoe  ")
        assert user.username == "johndoe"

    def test_chain_strip_lower_slug(self):
        """Test chaining strip, lower, then slug."""

        class Article(BaseModel):
            slug: Field.field(transforms=[
                lambda x: x.strip(),
                lambda x: x.lower(),
                lambda s: String.slug(s)
            ])

        article = Article(slug="  Hello World!  ")
        assert article.slug == "hello-world"

    def test_chain_strip_truncate(self):
        """Test chaining strip then truncate."""

        class Post(BaseModel):
            title: Field.field(transforms=[
                lambda x: x.strip(),
                lambda s: String.truncate(s, length=10)
            ])

        post = Post(title="  This is a long title  ")
        assert post.title == "This is..."

    def test_chain_preserves_order(self):
        """Test that transforms are applied in order."""

        class Data(BaseModel):
            value: Field.field(transforms=[
                lambda x: x + "A",
                lambda x: x + "B",
                lambda x: x + "C"
            ])

        data = Data(value="")
        assert data.value == "ABC"


class TestIntegerTransforms:
    """Tests for Field.field(transforms=) with Integer utility methods."""

    def test_integer_clamp_max(self):
        """Test Integer.clamp with max value."""

        class Product(BaseModel):
            quantity: Field.field(base_type=int, transforms=lambda x: Integer.clamp(x, min_val=0, max_val=100))

        product = Product(quantity=150)
        assert product.quantity == 100

    def test_integer_clamp_min(self):
        """Test Integer.clamp with min value."""

        class Product(BaseModel):
            quantity: Field.field(base_type=int, transforms=lambda x: Integer.clamp(x, min_val=0, max_val=100))

        product = Product(quantity=-10)
        assert product.quantity == 0

    def test_integer_clamp_in_range(self):
        """Test Integer.clamp with value in range."""

        class Product(BaseModel):
            quantity: Field.field(base_type=int, transforms=lambda x: Integer.clamp(x, min_val=0, max_val=100))

        product = Product(quantity=50)
        assert product.quantity == 50

    def test_integer_abs(self):
        """Test Integer.abs transformation."""

        class Data(BaseModel):
            value: Field.field(base_type=int, transforms=lambda x: abs(x))

        data = Data(value=-42)
        assert data.value == 42


class TestNoneHandling:
    """Tests for None value handling."""

    def test_skip_none_default(self):
        """Test that None is skipped by default."""

        class User(BaseModel):
            name: Field.field(transforms=lambda x: x.strip()) | None = None

        user = User(name=None)
        assert user.name is None

    def test_skip_none_explicit(self):
        """Test explicit skip_none=True."""

        class User(BaseModel):
            name: Field.field(transforms=lambda x: x.strip(), skip_none=True) | None = None

        user = User(name=None)
        assert user.name is None

    def test_skip_none_false_raises(self):
        """Test skip_none=False attempts to transform None and catches the error."""

        def transform_requires_string(x: str) -> str:
            # This will fail if x is None
            return x.strip()

        class User(BaseModel):
            name: Field.field(transforms=transform_requires_string, skip_none=False)

        # With skip_none=False and a non-optional field, passing None will attempt transform
        # which will fail since None doesn't have .strip()
        with pytest.raises(ValidationError):
            User(name=None)


class TestErrorHandling:
    """Tests for error handling in transforms."""

    def test_transform_error_provides_context(self):
        """Test that transform errors provide helpful context."""

        def bad_transform(x: str) -> str:
            raise RuntimeError("Something went wrong")

        class Data(BaseModel):
            value: Field.field(transforms=bad_transform)

        with pytest.raises(ValidationError) as exc_info:
            Data(value="test")

        errors = exc_info.value.errors()
        assert "bad_transform failed" in str(errors[0]["ctx"]["error"])

    def test_transform_chain_error_on_second(self):
        """Test error in second transform of chain."""

        def first_ok(x: str) -> str:
            return x.upper()

        def second_fails(x: str) -> str:
            raise ValueError("Failed")

        class Data(BaseModel):
            value: Field.field(transforms=[first_ok, second_fails])

        with pytest.raises(ValidationError) as exc_info:
            Data(value="test")

        errors = exc_info.value.errors()
        assert "second_fails failed" in str(errors[0]["ctx"]["error"])


class TestWithPydanticFeatures:
    """Tests for integration with Pydantic features."""

    def test_with_default_value(self):
        """Test transform with default value."""

        class User(BaseModel):
            name: Field.field(transforms=lambda x: x.strip()) = "Guest"

        user = User()
        assert user.name == "Guest"

        user = User(name="  John  ")
        assert user.name == "John"

    def test_with_optional_field(self):
        """Test transform with optional field."""

        class User(BaseModel):
            nickname: Field.field(transforms=lambda x: x.strip()) | None = None

        user = User()
        assert user.nickname is None

        user = User(nickname="  Bob  ")
        assert user.nickname == "Bob"

    def test_multiple_fields_different_transforms(self):
        """Test multiple fields with different transforms."""

        class Article(BaseModel):
            title: Field.field(transforms=[lambda x: x.strip(), lambda x: x.capitalize()])
            slug: Field.field(transforms=[lambda x: x.strip(), lambda x: x.lower(), lambda s: String.slug(s)])
            summary: Field.field(transforms=[lambda x: x.strip(), lambda s: String.truncate(s, length=50)])

        article = Article(
            title="  hello world  ",
            slug="  Hello World!  ",
            summary="  This is a very long summary that should be truncated at fifty chars  "
        )

        assert article.title == "Hello world"
        assert article.slug == "hello-world"
        assert len(article.summary) <= 50


class TestComplexTransforms:
    """Tests for complex transformation scenarios."""

    def test_custom_lambda_transform(self):
        """Test with custom lambda function."""

        class Data(BaseModel):
            doubled: Field.field(base_type=int, transforms=lambda x: x * 2)

        data = Data(doubled=5)
        assert data.doubled == 10

    def test_strip_and_default_if_empty(self):
        """Test strip and provide default if empty."""

        def strip_or_default(s: str) -> str:
            stripped = s.strip()
            return stripped if stripped else "default"

        class User(BaseModel):
            name: Field.field(transforms=strip_or_default)

        user = User(name="  ")
        assert user.name == "default"

        user = User(name="  John  ")
        assert user.name == "John"

    def test_nested_model_with_transforms(self):
        """Test transforms in nested models."""

        class Address(BaseModel):
            city: Field.field(transforms=[lambda x: x.strip(), lambda x: x.title()])
            state: Field.field(transforms=[lambda x: x.strip(), lambda x: x.upper()])

        class User(BaseModel):
            name: Field.field(transforms=lambda x: x.strip())
            address: Address

        user = User(
            name="  john  ",
            address={"city": "  new york  ", "state": "  ny  "}
        )

        assert user.name == "john"
        assert user.address.city == "New York"
        assert user.address.state == "NY"

    def test_list_of_transformed_values(self):
        """Test transform on list field items."""

        # Note: This transforms the list itself, not items
        class Data(BaseModel):
            tags: Field.field(base_type=list, transforms=lambda tags: [t.strip().lower() for t in tags])

        data = Data(tags=["  Python  ", "  Django  ", "  FastAPI  "])
        assert data.tags == ["python", "django", "fastapi"]


class TestFieldMethod:
    """Tests for Field.field() combining transforms and validators."""

    def test_field_with_transforms_only(self):
        """Test field with only transforms."""

        class User(BaseModel):
            name: Field.field(transforms=lambda x: x.strip())

        user = User(name="  John  ")
        assert user.name == "John"

    def test_field_with_validators_only(self):
        """Test field with only validators."""

        class User(BaseModel):
            email: Field.field(validators=Validator.email())

        user = User(email="test@example.com")
        assert user.email == "test@example.com"

        with pytest.raises(ValidationError):
            User(email="invalid")

    def test_field_with_both_transforms_and_validators(self):
        """Test field with both transforms and validators."""

        class User(BaseModel):
            email: Field.field(
                transforms=[lambda x: x.strip(), lambda x: x.lower()],
                validators=Validator.email()
            )

        user = User(email="  Test@EXAMPLE.COM  ")
        assert user.email == "test@example.com"

    def test_field_with_multiple_validators(self):
        """Test field with multiple validators."""

        class User(BaseModel):
            username: Field.field(
                transforms=lambda x: x.strip(),
                validators=[
                    Validator.min_length(length=3),
                    Validator.max_length(length=20)
                ]
            )

        user = User(username="  john  ")
        assert user.username == "john"

        with pytest.raises(ValidationError):
            User(username="ab")

        with pytest.raises(ValidationError):
            User(username="a" * 25)

    def test_field_with_base_type(self):
        """Test field with custom base type."""

        class Config(BaseModel):
            count: Field.field(
                base_type=int,
                transforms=lambda x: Integer.clamp(x, min_val=0, max_val=100)
            )

        config = Config(count=150)
        assert config.count == 100

    def test_field_transforms_applied_before_validators(self):
        """Test that transforms are applied before validators."""

        class User(BaseModel):
            email: Field.field(
                transforms=[lambda x: x.strip(), lambda x: x.lower()],
                validators=Validator.email()
            )

        # Whitespace and uppercase would fail validation, but transforms fix it
        user = User(email="  TEST@EXAMPLE.COM  ")
        assert user.email == "test@example.com"


class TestRealWorldScenarios:
    """Tests for real-world usage scenarios."""

    def test_user_registration_form(self):
        """Test typical user registration form transformations."""

        class UserRegistration(BaseModel):
            username: Field.field(transforms=[lambda x: x.strip(), lambda x: x.lower()])
            email: Field.field(transforms=[lambda x: x.strip(), lambda x: x.lower()])
            display_name: Field.field(transforms=[lambda x: x.strip(), lambda x: x.title()])

        user = UserRegistration(
            username="  JohnDoe123  ",
            email="  John.Doe@EXAMPLE.COM  ",
            display_name="  john doe  "
        )

        assert user.username == "johndoe123"
        assert user.email == "john.doe@example.com"
        assert user.display_name == "John Doe"

    def test_user_registration_with_field(self):
        """Test user registration using field() method."""

        class UserRegistration(BaseModel):
            username: Field.field(
                transforms=[lambda x: x.strip(), lambda x: x.lower()],
                validators=[
                    Validator.min_length(length=3),
                    Validator.max_length(length=20)
                ]
            )
            email: Field.field(
                transforms=[lambda x: x.strip(), lambda x: x.lower()],
                validators=Validator.email()
            )

        user = UserRegistration(
            username="  JohnDoe123  ",
            email="  Test@EXAMPLE.COM  "
        )

        assert user.username == "johndoe123"
        assert user.email == "test@example.com"

    def test_blog_post_processing(self):
        """Test blog post title and slug generation."""

        class BlogPost(BaseModel):
            title: Field.field(transforms=[
                lambda x: x.strip(),
                lambda s: String.truncate(s, length=100, suffix="...")
            ])
            slug: Field.field(transforms=[
                lambda x: x.strip(),
                lambda x: x.lower(),
                lambda s: String.slug(s)
            ])

        post = BlogPost(
            title="  This is an incredibly long blog post title that really should be truncated for display purposes  ",
            slug="  This is an incredibly long blog post title!  "
        )

        assert len(post.title) <= 100
        assert post.slug == "this-is-an-incredibly-long-blog-post-title"

    def test_product_normalization(self):
        """Test product data normalization."""

        class Product(BaseModel):
            sku: Field.field(transforms=[lambda x: x.strip(), lambda x: x.upper()])
            name: Field.field(transforms=[lambda x: x.strip(), lambda x: x.title()])
            quantity: Field.field(base_type=int, transforms=lambda x: Integer.clamp(x, min_val=0, max_val=9999))

        product = Product(
            sku="  abc-123  ",
            name="  wireless mouse  ",
            quantity=15000
        )

        assert product.sku == "ABC-123"
        assert product.name == "Wireless Mouse"
        assert product.quantity == 9999
