# Pydantic Model with Transform/Validate API

Enhanced Pydantic BaseModel with Config-based transforms, validators, and auto-injection features.

## Installation

```python
from utils.pydantic_model import PydanticModel, ValidationError
```

## Features

This package extends Pydantic's `BaseModel` with:

- **Config-based transforms** - Apply transforms to multiple fields via `Config.apply_transforms`
- **Config-based validators** - Apply validators to multiple fields via `Config.apply_validators`
- **Global validators** - Cross-field validation via `Config.global_validators`
- **Auto-injection** - Field values automatically injected into validators/transforms by parameter name
- **Custom JSON serializer** - Override JSON serialization via `Config.json_serializer`

All standard Pydantic features work normally.

## Quick Start

```python
from utils.pydantic_model import PydanticModel

class User(PydanticModel):
    class Config:
        # Transform multiple fields
        apply_transforms = {
            ("email", "username"): [str.strip, str.lower]
        }

        # Validate multiple fields
        apply_validators = {
            ("email",): lambda x: "@" in x,
            ("age",): lambda x: 0 <= x <= 120
        }

        # Global cross-field validation
        global_validators = [
            lambda v: v["age"] >= 18 or v["role"] != "admin"
        ]

    email: str
    username: str
    age: int
    role: str = "user"

user = User(email="  ADMIN@EXAMPLE.COM  ", username="  ADMIN  ", age=25)
print(user.email)     # "admin@example.com"
print(user.username)  # "admin"
```

## Config-based Transforms

Apply transforms to multiple fields using `Config.apply_transforms`:

```python
class User(PydanticModel):
    class Config:
        apply_transforms = {
            # Apply to multiple fields
            ("email", "username"): [str.strip, str.lower],

            # Transform chains
            ("title",): [str.strip, str.title],

            # Transforms with arguments (tuple syntax)
            ("summary",): [(truncate, {"max_length": 100})]
        }

    email: str
    username: str
    title: str
    summary: str
```

**Transform execution:**
- Transforms run **before** Pydantic validation
- Applied in sequence (left to right)
- Each transform receives the output of the previous one

## Config-based Validators

Apply validators to multiple fields using `Config.apply_validators`:

```python
from utils import Validator

class User(PydanticModel):
    class Config:
        apply_validators = {
            ("email",): Validator.email,
            ("age",): lambda x: 0 <= x <= 120,

            # Multiple validators per field
            ("password",): [
                lambda x: len(x) >= 8,
                lambda x: any(c.isupper() for c in x)
            ],

            # Validators with arguments (tuple syntax)
            ("username",): [(min_length, {"length": 3})]
        }

    email: str
    age: int
    password: str
    username: str
```

**Validator execution:**
- Validators run **after** Pydantic validation and transforms
- All validators must pass (return `True` or not return `False`)
- Runs before global validators

## Global Validators

Cross-field validation using `Config.global_validators`:

```python
class User(PydanticModel):
    class Config:
        global_validators = [
            # Admins must be 18+
            lambda v: v["age"] >= 18 or v["role"] != "admin",

            # Passwords must match
            lambda v: v["password"] == v["confirm_password"]
        ]

    age: int
    role: str
    password: str
    confirm_password: str
```

**Global validator execution:**
- Receives dict of all field values
- Runs **after** field transforms and validators
- All global validators must pass

## Auto-injection

Validators and transforms can reference other fields by parameter name:

```python
def validate_password_match(password: str, confirm_password: str) -> bool:
    """Auto-injected: confirm_password from model fields."""
    return password == confirm_password

def format_full_name(first_name: str, last_name: str) -> str:
    """Auto-injected: last_name from model fields."""
    return f"{first_name} {last_name}"

class User(PydanticModel):
    class Config:
        apply_validators = {
            ("password",): validate_password_match
        }
        apply_transforms = {
            ("display_name",): format_full_name  # Uses first_name field
        }

    first_name: str
    last_name: str
    password: str
    confirm_password: str
    display_name: str = ""

user = User(
    first_name="John",
    last_name="Doe",
    password="secret123",
    confirm_password="secret123",
    display_name=""  # Will be transformed to "John Doe"
)
```

**How it works:**
- Function parameters are matched against field names
- Matching fields are automatically injected
- Special parameter `all_values: dict` injects all field values

### Context-aware with all_values

Use `all_values` parameter to access all fields:

```python
def validate_admin_email(email: str, all_values: dict) -> bool:
    """Admins must use company email."""
    if all_values.get("role") == "admin":
        return email.endswith("@company.com")
    return True

class User(PydanticModel):
    class Config:
        apply_validators = {
            ("email",): validate_admin_email
        }

    email: str
    role: str
```

## Custom JSON Serializer

Override JSON serialization for custom types via `Config.json_serializer`:

```python
from datetime import datetime

def custom_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Cannot serialize {type(obj)}")

class Article(PydanticModel):
    class Config:
        json_serializer = custom_serializer

    title: str
    published: datetime

article = Article(title="Hello", published=datetime.now())
json_str = article.json()  # Uses custom serializer for datetime objects
```

**Note:** For standard serialization, use Pydantic's native methods:
- `model_dump()` - Convert to dict
- `model_dump_json()` - Convert to JSON string
- `model_validate()` - Create from dict
- `model_validate_json()` - Create from JSON string

## Using Pydantic ConfigDict

Pass Pydantic configuration via `Config.config_dict`:

```python
from pydantic import ConfigDict

class User(PydanticModel):
    class Config:
        apply_transforms = {
            ("email",): [str.lower]
        }

        # Pydantic options
        config_dict = {
            "extra": "forbid",  # Reject extra fields
            "str_strip_whitespace": True,
            "validate_assignment": True
        }

    email: str
    age: int
```

Or use `model_config` directly:

```python
from pydantic import ConfigDict

class User(PydanticModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    email: str
    age: int
```

## Complete Config Example

```python
from utils.pydantic_model import PydanticModel
from utils import Validator

class User(PydanticModel):
    class Config:
        # Transform fields
        apply_transforms = {
            ("email", "username"): [str.strip, str.lower],
            ("bio",): [(truncate, {"max_length": 500})]
        }

        # Validate fields
        apply_validators = {
            ("email",): Validator.email,
            ("age",): lambda x: 0 <= x <= 120,
            ("password",): [
                lambda x: len(x) >= 8,
                lambda x: any(c.isupper() for c in x)
            ]
        }

        # Global cross-field validation
        global_validators = [
            lambda v: v["age"] >= 18 or v["role"] != "admin",
            lambda v: v["password"] == v["confirm_password"]
        ]

        # Custom JSON serializer
        json_serializer = custom_serializer_function

        # Pydantic options
        config_dict = {
            "extra": "forbid",
            "str_strip_whitespace": True
        }

    email: str
    username: str
    bio: str
    age: int
    role: str
    password: str
    confirm_password: str
```

## Error Handling

```python
from utils.pydantic_model import ValidationError

try:
    user = User(email="invalid", age=25)
except ValidationError as e:
    print(e)  # Validation error message
    print(e.pydantic_error)  # Access underlying Pydantic error
```

## Execution Order

When creating a model instance:

1. **Transforms** run first (on input data)
2. **Pydantic validation** (type checking, Field constraints)
3. **Custom validators** (from `apply_validators`)
4. **Global validators** (from `global_validators`)

This ensures transforms prepare data before validation occurs.
