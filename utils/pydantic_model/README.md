# Pydantic Model System

A Pydantic-based Model system that preserves the clean transform/validate API from `utils.model` while leveraging Pydantic v2's performance and ecosystem benefits.

## Overview

`PydanticModel` extends Pydantic's `BaseModel` to provide:
- **Config-based transforms and validators** - Apply transforms/validators to multiple fields via Config
- **Auto-injection** - Field values automatically injected into validators/transforms
- **Global validators** - Cross-field validation logic
- **Full Pydantic compatibility** - Works with Field, computed_field, and all Pydantic features

## Installation

```python
from utils.pydantic_model import PydanticModel, ValidationError
from pydantic import Field, computed_field  # Use Pydantic's Field and computed_field
```

## Basic Usage

### Simple Model

```python
from utils.pydantic_model import PydanticModel

class User(PydanticModel):
    email: str
    age: int
    role: str = "user"  # Default value

user = User(email="admin@example.com", age=25)
print(user.email)  # "admin@example.com"
```

### Config-based Transforms

Apply transforms to multiple fields using the `Config` class:

```python
from utils.pydantic_model import PydanticModel
from utils import String

class User(PydanticModel):
    class Config:
        apply_transforms = {
            ("email", "username"): [str.strip, str.lower]
        }

    email: str
    username: str
    age: int

user = User(email="  ADMIN@EXAMPLE.COM  ", username="  ADMIN  ", age=25)
print(user.email)     # "admin@example.com"
print(user.username)  # "admin"
```

### Config-based Validators

Apply validators to multiple fields:

```python
from utils.pydantic_model import PydanticModel
from utils import Validator

class User(PydanticModel):
    class Config:
        apply_validators = {
            ("email",): Validator.email,
            ("age",): lambda x: 0 <= x <= 120
        }

    email: str
    age: int

# Raises ValidationError if email is invalid or age out of range
user = User(email="admin@example.com", age=25)
```

### Global Validators

Validate across multiple fields:

```python
from utils.pydantic_model import PydanticModel

class User(PydanticModel):
    class Config:
        global_validators = [
            lambda v: v["age"] >= 18 or v["role"] != "admin"
        ]

    age: int
    role: str

# Raises ValidationError: admins must be 18+
user = User(age=16, role="admin")  # ❌ Error

# OK: non-admin can be under 18
user = User(age=16, role="user")   # ✅ OK
```

## Advanced Features

### Auto-injection

Validators and transforms can reference other fields by name:

```python
from utils.pydantic_model import PydanticModel

def validate_password_match(password: str, confirm_password: str) -> bool:
    """Auto-injected confirm_password from other field."""
    return password == confirm_password

class User(PydanticModel):
    class Config:
        apply_validators = {
            ("password",): validate_password_match
        }

    password: str
    confirm_password: str

user = User(password="secret123", confirm_password="secret123")  # ✅ OK
user = User(password="secret123", confirm_password="different")  # ❌ Error
```

### Context-aware Validation

Use `all_values` parameter to access all field values:

```python
from utils.pydantic_model import PydanticModel

def validate_email_domain(email: str, all_values: dict) -> bool:
    """Check email domain matches organization."""
    if all_values.get("role") == "admin":
        return email.endswith("@company.com")
    return True

class User(PydanticModel):
    class Config:
        apply_validators = {
            ("email",): validate_email_domain
        }

    email: str
    role: str

user = User(email="admin@company.com", role="admin")  # ✅ OK
user = User(email="user@gmail.com", role="user")      # ✅ OK
user = User(email="admin@gmail.com", role="admin")    # ❌ Error
```

### Transform Chains

Apply multiple transforms in sequence:

```python
from utils.pydantic_model import PydanticModel
from utils import String

class Article(PydanticModel):
    class Config:
        apply_transforms = {
            ("title",): [str.strip, str.title],
            ("slug",): [str.strip, str.lower, lambda s: s.replace(" ", "-")]
        }

    title: str
    slug: str

article = Article(title="  hello world  ", slug="  Hello World  ")
print(article.title)  # "Hello World"
print(article.slug)   # "hello-world"
```

### Transforms with Arguments

Pass arguments to transforms using tuple syntax:

```python
from utils.pydantic_model import PydanticModel

def truncate(text: str, max_length: int) -> str:
    return text[:max_length]

class Article(PydanticModel):
    class Config:
        apply_transforms = {
            ("summary",): [(truncate, {"max_length": 100})]
        }

    summary: str

article = Article(summary="x" * 200)
print(len(article.summary))  # 100
```

### Extra Fields Handling

Control how extra/unknown fields are handled:

```python
from utils.pydantic_model import PydanticModel

# Store mode (default) - stores extra fields
class User(PydanticModel):
    class Config:
        extra_fields_mode = "store"  # default

    name: str
    age: int

user = User(name="Alice", age=25, role="admin")
print(user.role)  # "admin"

# Strict mode - raises error on extra fields
class StrictUser(PydanticModel):
    class Config:
        extra_fields_mode = "strict"

    name: str
    age: int

user = StrictUser(name="Alice", age=25, role="admin")  # ❌ ValidationError

# Ignore mode - silently ignores extra fields
class IgnoreUser(PydanticModel):
    class Config:
        extra_fields_mode = "ignore"

    name: str
    age: int

user = IgnoreUser(name="Alice", age=25, role="admin")  # ✅ OK
# user.role does not exist
```

### Pydantic Field Options

Use Pydantic's `Field` for additional options:

```python
from utils.pydantic_model import PydanticModel
from pydantic import Field

class User(PydanticModel):
    email: str = Field(description="User email address")
    age: int = Field(ge=0, le=120, description="User age")
    name: str = Field(alias="full_name")

user = User(full_name="John Doe", email="john@example.com", age=25)
print(user.name)  # "John Doe"
```

### Computed Fields

Use Pydantic's `@computed_field` decorator:

```python
from utils.pydantic_model import PydanticModel
from pydantic import computed_field

class User(PydanticModel):
    first_name: str
    last_name: str

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

user = User(first_name="John", last_name="Doe")
print(user.full_name)  # "John Doe"
```

## Serialization

### to_dict()

```python
user = User(email="admin@example.com", age=25, role="admin")

# Basic dict conversion
data = user.to_dict()

# Exclude None values
data = user.to_dict(exclude_none=True)

# Exclude specific fields
data = user.to_dict(exclude_fields=["role"])
```

### json()

```python
# Serialize to JSON string
json_str = user.json()

# With exclusions
json_str = user.json(exclude_none=True, exclude_fields=["role"])

# Custom serializer
class Config:
    json_serializer = custom_serializer_func

json_str = user.json()
```

### from_dict() / model_validate()

```python
# From dictionary
user = User.from_dict({"email": "admin@example.com", "age": 25})

# Pydantic-compatible alias
user = User.model_validate({"email": "admin@example.com", "age": 25})

# From JSON string
user = User.model_validate_json('{"email": "admin@example.com", "age": 25}')
```

## Configuration Options

### All Config Options

```python
class User(PydanticModel):
    class Config:
        # Extra fields handling: "store" (default), "strict", or "ignore"
        extra_fields_mode = "store"

        # Apply transforms to multiple fields
        apply_transforms = {
            ("email", "username"): [str.strip, str.lower]
        }

        # Apply validators to multiple fields
        apply_validators = {
            ("email",): Validator.email,
            ("age",): lambda x: 0 <= x <= 120
        }

        # Global validators with cross-field logic
        global_validators = [
            lambda v: v["age"] >= 18 or v["role"] != "admin"
        ]

        # Custom JSON serializer for all json() calls
        json_serializer = custom_serializer_function

    email: str
    username: str
    age: int
    role: str
```

### Custom JSON Serializer

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
json_str = article.json()  # Uses custom serializer for datetime
```

## Key Benefits Over Pure-Python Model

1. **Performance** - Pydantic v2 is built on Rust (10-50x faster validation)
2. **Type Safety** - Better integration with mypy/pyright
3. **JSON Schema** - Can generate schemas for API documentation
4. **Ecosystem** - Compatible with FastAPI, LangChain, and other Pydantic-based tools
5. **Serialization** - Pydantic's optimized JSON serialization

## Migration from utils.model

**Only Two Changes:**

1. Change base class from `Model` to `PydanticModel`
2. Move field-level transforms/validators to Config

```python
# Before (utils.model)
from utils.model import Model, StringField

class User(Model):
    email: str = StringField(
        transform=[str.strip, str.lower],
        validate=Validator.email
    )

# After (utils.pydantic_model)
from utils.pydantic_model import PydanticModel
from utils import Validator

class User(PydanticModel):
    class Config:
        apply_transforms = {
            ("email",): [str.strip, str.lower]
        }
        apply_validators = {
            ("email",): Validator.email
        }

    email: str
```

## Error Handling

```python
from utils.pydantic_model import ValidationError

try:
    user = User(email="invalid", age=25)
except ValidationError as e:
    print(e)  # Validation error details
    print(e.pydantic_error)  # Access underlying Pydantic error
```

## Recommendation

**Use `PydanticModel` for:**
- Production APIs (FastAPI integration)
- Performance-critical applications
- Projects requiring JSON Schema
- Team projects (better IDE support)
- New greenfield projects

**Use Pure `Model` for:**
- Internal scripts/tools
- Existing codebases (no migration needed)
- When you want zero Pydantic dependency
- Educational/learning purposes
