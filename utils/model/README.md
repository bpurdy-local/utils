# Model System

A lightweight, Pydantic-inspired validation and serialization library with a clean API for defining validated data models with automatic transforms and validation.

## Table of Contents

- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Field Types](#field-types)
- [Validation](#validation)
- [Transforms](#transforms)
- [Advanced Features](#advanced-features)
- [Configuration](#configuration)
- [API Reference](#api-reference)

## Quick Start

```python
from utils import Model, StringField, IntField, ValidationError
from utils import String, Validator

class User(Model):
    email: StringField = StringField(
        transform=[String.strip, String.lower],
        validate=Validator.email
    )
    age: IntField = IntField()
    name: StringField | None = None  # Optional field
    role: StringField = StringField(default="user")  # With default

# Automatic transform + validation on init
user = User(email="  ADMIN@EXAMPLE.COM  ", age=25)
# user.email -> "admin@example.com"

# Re-validates on assignment
user.age = 30  # OK
user.age = 150  # Raises ValidationError

# Dict conversion
data = user.to_dict()
user2 = User.from_dict(data)
```

## Core Concepts

### Defining Models

Models are defined by subclassing `Model` and declaring fields with type annotations:

```python
from utils import Model, StringField, IntField, FloatField, BoolField

class Product(Model):
    name: StringField = StringField()
    price: FloatField = FloatField()
    quantity: IntField = IntField()
    in_stock: BoolField = BoolField()
```

### Field Types

The Model system provides several built-in field types:

#### Primitive Fields

```python
from utils import StringField, IntField, FloatField, BoolField

class User(Model):
    name: StringField = StringField()        # String values
    age: IntField = IntField()              # Integer values
    score: FloatField = FloatField()        # Float values
    active: BoolField = BoolField()         # Boolean values
```

#### Container Fields

```python
from utils import ListField, DictField

class Article(Model):
    tags: ListField = ListField(
        item_type=str,
        min_length=1,
        max_length=10
    )
    metadata: DictField = DictField(
        key_type=str,
        value_type=str
    )
```

#### Generic Field

For custom objects or types without specific field classes:

```python
from utils import Field
from datetime import datetime

class Event(Model):
    name: StringField = StringField()
    timestamp: Field = Field()  # Can store any type

event = Event(name="Meeting", timestamp=datetime.now())
```

#### Nested Models

```python
from utils import ModelField

class Address(Model):
    street: StringField = StringField()
    city: StringField = StringField()

class Person(Model):
    name: StringField = StringField()
    address: ModelField = ModelField(Address)

# Or using generic Field
class Person(Model):
    name: StringField = StringField()
    address: Field = Field()

# Both work with dict input
person = Person(
    name="Alice",
    address={"street": "123 Main St", "city": "Springfield"}
)
```

### Optional Fields

Fields can be marked as optional using Python's union type syntax:

```python
class User(Model):
    name: StringField = StringField()
    nickname: StringField | None = None  # Optional field

user = User(name="Alice")
user.nickname  # None

user = User(name="Alice", nickname="Ali")
user.nickname  # "Ali"
```

### Default Values

Fields can have default values:

```python
class User(Model):
    name: StringField = StringField()
    role: StringField = StringField(default="user")

user = User(name="Alice")
user.role  # "user"

user = User(name="Bob", role="admin")
user.role  # "admin"
```

### Type Coercion

Fields automatically convert compatible types:

```python
class User(Model):
    name: StringField = StringField()
    age: IntField = IntField()

user = User(name=123, age="25")
user.name  # "123" (converted from int)
user.age   # 25 (converted from string)

# BoolField handles many string formats
class Config(Model):
    enabled: BoolField = BoolField()

config = Config(enabled="true")   # True
config = Config(enabled="yes")    # True
config = Config(enabled="1")      # True
config = Config(enabled="false")  # False
config = Config(enabled="no")     # False
config = Config(enabled="0")      # False
```

## Validation

### Basic Validation

Add validators to ensure field values meet requirements:

```python
from utils import Validator

def is_positive(value: int) -> bool:
    return value > 0

class Product(Model):
    name: StringField = StringField(validate=Validator.email)
    price: FloatField = FloatField(validate=is_positive)

product = Product(name="test@example.com", price=19.99)  # OK
product = Product(name="invalid", price=19.99)  # Raises ValidationError
```

### Validators with Arguments

Pass arguments to validators using tuple syntax:

```python
def in_range(value: int, *, min: int, max: int) -> bool:
    return min <= value <= max

class User(Model):
    age: IntField = IntField(validate=(in_range, {"min": 0, "max": 120}))

user = User(age=25)   # OK
user = User(age=150)  # Raises ValidationError
```

### Multiple Validators

Chain multiple validators together:

```python
def not_empty(text: str) -> bool:
    return len(text.strip()) > 0

def max_length(text: str, *, length: int) -> bool:
    return len(text) <= length

class User(Model):
    email: StringField = StringField(
        validate=[
            Validator.email,
            not_empty,
            (max_length, {"length": 100})
        ]
    )
```

### Context-Aware Validators

Validators can access other field values:

```python
def validate_password_not_username(password: str, *, all_values: dict) -> bool:
    """Validator that checks password doesn't match username."""
    username = all_values.get("username", "")
    if username and password.lower() == username.lower():
        raise ValidationError("Password cannot be the same as username")
    return True

class User(Model):
    username: StringField = StringField()
    password: StringField = StringField(validate=validate_password_not_username)
```

### Auto-Injection

Validators can automatically receive field values as parameters:

```python
def validate_email_domain(email: str, *, domain: str) -> bool:
    """Validator that checks email matches expected domain."""
    if not email.endswith(f"@{domain}"):
        raise ValidationError(f"Email must be from domain {domain}")
    return True

class User(Model):
    domain: StringField = StringField()
    email: StringField = StringField(validate=validate_email_domain)
    # The 'domain' parameter is auto-injected from the domain field

user = User(domain="example.com", email="alice@example.com")  # OK
user = User(domain="example.com", email="alice@other.com")    # Error
```

## Transforms

Transforms modify field values before validation:

### Basic Transforms

```python
from utils import String

class User(Model):
    email: StringField = StringField(transform=[String.strip, String.lower])

user = User(email="  ADMIN@EXAMPLE.COM  ")
user.email  # "admin@example.com"
```

### Transforms with Arguments

```python
def truncate(text: str, *, length: int) -> str:
    return String.truncate(text, length=length, suffix="")

class User(Model):
    name: StringField = StringField(transform=[(truncate, {"length": 10})])

user = User(name="Alexander")
user.name  # "Alexander" (truncated to 10 chars)
```

### Transform Order

Transforms run before validators:

```python
class User(Model):
    email: StringField = StringField(
        transform=[String.strip, String.lower],
        validate=Validator.email
    )

# Email is stripped and lowercased before validation
user = User(email="  ADMIN@EXAMPLE.COM  ")
user.email  # "admin@example.com"
```

### Transforms that Modify Values

Transforms can clamp, normalize, or modify values:

```python
from utils import Integer

def clamp(value: int, *, min: int, max: int) -> int:
    return Integer.clamp(value, min_val=min, max_val=max)

class Config(Model):
    volume: IntField = IntField(transform=[(clamp, {"min": 0, "max": 100})])

config = Config(volume=150)
config.volume  # 100 (clamped to max)

config = Config(volume=-10)
config.volume  # 0 (clamped to min)
```

## Advanced Features

### Computed Fields

Define read-only fields calculated from other fields:

```python
from utils import computed_field

class User(Model):
    first_name: StringField = StringField()
    last_name: StringField = StringField()

    @computed_field
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @computed_field(alias="displayName")
    def display_name(self) -> str:
        return self.full_name.upper()

user = User(first_name="Alice", last_name="Smith")
user.full_name      # "Alice Smith"
user.display_name   # "ALICE SMITH"

# Computed fields appear in serialization
data = user.to_dict()
# {"first_name": "Alice", "last_name": "Smith", "full_name": "Alice Smith", "displayName": "ALICE SMITH"}
```

### Field Aliases

Use different names for serialization:

```python
class User(Model):
    user_name: StringField = StringField(alias="userName")
    email_address: StringField = StringField(alias="emailAddress")

user = User(user_name="alice", email_address="alice@example.com")

data = user.to_dict()
# {"userName": "alice", "emailAddress": "alice@example.com"}

# Can deserialize using aliases
user2 = User.from_dict({"userName": "bob", "emailAddress": "bob@example.com"})
```

### Alias Generator

Automatically generate aliases for all fields:

```python
from utils.model import to_camel

class User(Model):
    class Config:
        alias_generator = to_camel

    user_name: StringField = StringField()
    email_address: StringField = StringField()
    is_active: BoolField = BoolField()

user = User(user_name="alice", email_address="alice@example.com", is_active=True)

data = user.to_dict()
# {"userName": "alice", "emailAddress": "alice@example.com", "isActive": True}
```

### Global Validators

Validate across multiple fields:

```python
def validate_age_role(values: dict) -> bool:
    if values["age"] < 18 and values["role"] == "admin":
        raise ValidationError("Admins must be 18 or older")
    return True

class User(Model):
    class Config:
        global_validators = [validate_age_role]

    age: IntField = IntField()
    role: StringField = StringField()

user = User(age=25, role="admin")  # OK
user = User(age=16, role="user")   # OK
user = User(age=16, role="admin")  # Raises ValidationError
```

### Bulk Transforms and Validators

Apply transforms/validators to multiple fields at once:

```python
class User(Model):
    class Config:
        apply_transforms = {
            ("email", "username"): [String.strip, String.lower],
        }
        apply_validators = {
            ("email", "username"): lambda x: len(x) > 0,
        }

    email: StringField = StringField()
    username: StringField = StringField()
    bio: StringField = StringField()

user = User(email="  ADMIN@EXAMPLE.COM  ", username="  ADMIN  ", bio="Hello")
# email -> "admin@example.com" (transformed)
# username -> "admin" (transformed)
# bio -> "Hello" (not affected)
```

### Extra Fields Handling

Control how unknown fields are handled:

```python
# Default: store unknown fields
class User(Model):
    name: StringField = StringField()

user = User(name="Alice", age=25, role="admin")
user._extra_fields  # {"age": 25, "role": "admin"}

# Strict: raise error on unknown fields
class StrictUser(Model):
    class Config:
        extra_fields_mode = "strict"

    name: StringField = StringField()

user = StrictUser(name="Alice", age=25)  # Raises ValidationError

# Ignore: silently ignore unknown fields
class IgnoreUser(Model):
    class Config:
        extra_fields_mode = "ignore"

    name: StringField = StringField()

user = IgnoreUser(name="Alice", age=25)  # age is silently ignored
user._extra_fields  # {}
```

### Serialization Control

Exclude fields from serialization:

```python
class User(Model):
    name: StringField = StringField()
    password: StringField = StringField(exclude=True)
    email: StringField = StringField(exclude_from_json=True)
    internal_id: StringField = StringField(exclude_from_dict=True)

user = User(name="Alice", password="secret", email="alice@example.com", internal_id="123")

user.to_dict()
# {"name": "Alice", "email": "alice@example.com"}
# (password excluded, internal_id excluded from dict)

user.json()
# {"name": "Alice"}
# (password excluded, email excluded from JSON)
```

### Custom Object Support

Store and serialize custom objects:

```python
from datetime import datetime
from decimal import Decimal

class Event(Model):
    name: StringField = StringField()
    timestamp: Field = Field()
    price: Field = Field()

event = Event(
    name="Conference",
    timestamp=datetime(2024, 1, 15, 10, 30),
    price=Decimal("99.99")
)

# Built-in serialization for common types
json_str = event.json()
# {"name": "Conference", "timestamp": "2024-01-15T10:30:00", "price": 99.99}

# Custom serializer for your own types
class Color:
    def __init__(self, r, g, b):
        self.r, self.g, self.b = r, g, b

def serialize_color(obj):
    if isinstance(obj, Color):
        return {"r": obj.r, "g": obj.g, "b": obj.b}
    raise TypeError

class Theme(Model):
    name: StringField = StringField()
    color: Field = Field()

theme = Theme(name="Sunset", color=Color(255, 128, 0))
json_str = theme.json(default=serialize_color)
# {"name": "Sunset", "color": {"r": 255, "g": 128, "b": 0}}

# Or set a default serializer for all json() calls via Config
class Theme(Model):
    class Config:
        json_serializer = serialize_color

    name: StringField = StringField()
    color: Field = Field()

theme = Theme(name="Sunset", color=Color(255, 128, 0))
json_str = theme.json()  # Uses Config serializer automatically
# {"name": "Sunset", "color": {"r": 255, "g": 128, "b": 0}}

# Per-call serializer still overrides Config serializer
json_str = theme.json(default=another_serializer)
```

## Configuration

Configure model behavior using the `Config` class:

```python
class User(Model):
    class Config:
        # Auto-generate aliases for all fields
        alias_generator = to_camel

        # Apply transforms to multiple fields
        apply_transforms = {
            ("email", "username"): [String.strip, String.lower]
        }

        # Apply validators to multiple fields
        apply_validators = {
            ("email", "username"): lambda x: len(x) > 0
        }

        # Global validators with cross-field logic
        global_validators = [
            lambda vals: vals["age"] >= 18 or vals["role"] != "admin"
        ]

        # Handle unknown fields: "store" (default), "strict", or "ignore"
        extra_fields_mode = "store"

        # Custom JSON serializer for all json() calls (can be overridden per-call)
        json_serializer = custom_serializer_function

    user_name: StringField = StringField()
    email: StringField = StringField()
    age: IntField = IntField()
    role: StringField = StringField()
```

## API Reference

### Model Methods

```python
# Initialization
user = User(name="Alice", age=25)

# Dict conversion
data = user.to_dict(exclude_none=True, exclude_fields=["password"])
user = User.from_dict({"name": "Alice", "age": 25})

# Pydantic-compatible aliases
user = User.model_validate({"name": "Alice", "age": 25})

# JSON serialization
json_str = user.json(exclude_none=True, exclude_fields=["password"], indent=2)
user = User.model_validate_json('{"name": "Alice", "age": 25}')

# Comparison
user1 == user2  # Compares using to_dict()

# String representation
str(user)   # User(name='Alice', age=25)
repr(user)  # User(name='Alice', age=25)
```

### Field Parameters

```python
Field(
    transform=None,           # Single function or list of transforms
    validate=None,            # Single function or list of validators
    default=None,             # Default value if not provided
    required=True,            # Whether field is required
    alias=None,               # Alternative name for serialization
    exclude=False,            # Exclude from all serialization
    exclude_from_dict=False,  # Exclude only from to_dict()
    exclude_from_json=False,  # Exclude only from json()
)
```

### ListField Parameters

```python
ListField(
    item_type=None,      # Type validation for list items
    item_validator=None, # Custom validator for each item
    min_length=None,     # Minimum number of items
    max_length=None,     # Maximum number of items
    **kwargs             # All Field parameters
)
```

### DictField Parameters

```python
DictField(
    key_type=None,       # Type validation for dict keys
    value_type=None,     # Type validation for dict values
    value_validator=None,# Custom validator for each value
    **kwargs             # All Field parameters
)
```

### ModelField Parameters

```python
ModelField(
    model_class,  # The Model class for nested instances
    **kwargs      # All Field parameters
)
```

## Best Practices

### 1. Use Type Hints

Always provide type annotations for IDE support and clarity:

```python
class User(Model):
    name: StringField = StringField()  # Good
    age: IntField = IntField()         # Good
```

### 2. Combine Transforms and Validators

Transforms run before validators, so clean data first:

```python
class User(Model):
    email: StringField = StringField(
        transform=[String.strip, String.lower],  # Clean first
        validate=Validator.email                  # Then validate
    )
```

### 3. Use Descriptive Validator Functions

Make validator errors clear:

```python
def validate_strong_password(password: str) -> bool:
    """Password must be at least 8 chars with uppercase, lowercase, and digit."""
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters")
    if not any(c.isupper() for c in password):
        raise ValidationError("Password must contain uppercase letter")
    if not any(c.islower() for c in password):
        raise ValidationError("Password must contain lowercase letter")
    if not any(c.isdigit() for c in password):
        raise ValidationError("Password must contain digit")
    return True
```

### 4. Leverage Auto-Injection

Reduce boilerplate by letting the system inject field values:

```python
# Instead of using all_values:
def old_validator(email: str, *, all_values: dict) -> bool:
    domain = all_values.get("domain")
    return email.endswith(f"@{domain}")

# Use auto-injection:
def new_validator(email: str, *, domain: str) -> bool:
    return email.endswith(f"@{domain}")

class User(Model):
    domain: StringField = StringField()
    email: StringField = StringField(validate=new_validator)
```

### 5. Use Global Validators for Cross-Field Logic

When validation depends on multiple fields:

```python
class User(Model):
    class Config:
        global_validators = [
            lambda vals: vals["age"] >= 18 or vals["role"] != "admin"
        ]

    age: IntField = IntField()
    role: StringField = StringField()
```

## Migration from Pydantic

The Model system provides Pydantic-compatible aliases:

```python
# Pydantic style
user = User.model_validate({"name": "Alice", "age": 25})
json_str = user.model_dump_json()
data = user.model_dump()

# Native style (also supported)
user = User.from_dict({"name": "Alice", "age": 25})
json_str = user.json()
data = user.to_dict()
```

## Examples

See [tests/test_model.py](../../../tests/test_model.py) for comprehensive examples covering all features.

## Architecture

The Model system is organized into focused modules:

- **exceptions.py** - ValidationError class
- **helpers.py** - Helper functions for context-aware calls
- **serialization.py** - JSON serialization and alias generation
- **metaclass.py** - ModelMeta for field processing
- **model.py** - Model base class
- **fields/** - Field type implementations
  - **base.py** - Field base class
  - **primitive.py** - String, Int, Float, Bool fields
  - **container.py** - List, Dict fields
  - **model_field.py** - Nested model support
  - **computed.py** - Computed field decorator

## License

Part of the utils library.
