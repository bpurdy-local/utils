# Feature Comparison: utils/model vs utils/pydantic_model

This document tracks feature parity between the pure-Python `utils.model` package and the Pydantic-based `utils.pydantic_model` package, including design decisions and rationale for any unsupported features.

## Overview

**utils/model** - Pure-Python validation and serialization library with custom field descriptors
**utils/pydantic_model** - Pydantic v2 BaseModel extension preserving the transform/validate API

## Feature Support Matrix

### ✅ Fully Supported Features

| Feature | utils/model | utils/pydantic_model | Notes |
|---------|-------------|----------------------|-------|
| **Config-based transforms** | ✅ | ✅ | Both support `Config.apply_transforms` for bulk transforms |
| **Config-based validators** | ✅ | ✅ | Both support `Config.apply_validators` for bulk validation |
| **Global validators** | ✅ | ✅ | Cross-field validation via `Config.global_validators` |
| **Auto-injection** | ✅ | ✅ | Field values auto-injected into validators/transforms |
| **Context-aware validation** | ✅ | ✅ | `all_values` parameter for accessing all fields |
| **Transform chains** | ✅ | ✅ | Multiple transforms in sequence |
| **Validator chains** | ✅ | ✅ | Multiple validators in sequence |
| **Transforms with arguments** | ✅ | ✅ | Tuple syntax: `(func, {"arg": value})` |
| **Validators with arguments** | ✅ | ✅ | Tuple syntax: `(func, {"arg": value})` |
| **Default values** | ✅ | ✅ | Both support field defaults |
| **Optional fields** | ✅ | ✅ | `field: str \| None = None` |
| **to_dict()** | ✅ | ✅ | Convert model to dictionary |
| **from_dict()** | ✅ | ✅ | Create model from dictionary |
| **json()** | ✅ | ✅ | Serialize to JSON string |
| **model_validate()** | ✅ | ✅ | Pydantic-compatible alias for from_dict |
| **model_validate_json()** | ✅ | ✅ | Create from JSON string |
| **exclude_none** | ✅ | ✅ | Exclude None values from serialization |
| **exclude_fields** | ✅ | ✅ | Exclude specific fields from serialization |
| **Custom JSON serializer** | ✅ | ✅ | Via `Config.json_serializer` |
| **Extra fields handling** | ✅ | ✅ | Both support store/strict/ignore via `Config.extra_fields_mode` |
| **Type coercion** | ✅ | ✅ | Both automatically convert compatible types |
| **Nested models** | ✅ | ✅ | Both support nested model instances |
| **Pydantic Field** | N/A | ✅ | Use Pydantic's Field() for constraints, aliases, descriptions |
| **Pydantic computed_field** | N/A | ✅ | Users can directly use Pydantic's @computed_field decorator |

### 🔄 Different Implementation

| Feature | utils/model | utils/pydantic_model | Why Different? |
|---------|-------------|----------------------|----------------|
| **Field-level transforms** | ✅ Custom field classes | ❌ Config-based only | Pydantic v2 uses Annotated types, not FieldInfo.metadata. Field-level transforms would require descriptor-based implementation which conflicts with Pydantic's internal machinery. Config-based approach is cleaner and more explicit. |
| **Field-level validators** | ✅ Custom field classes | ❌ Config-based only | Same reason as transforms. Pydantic v2's validation happens via annotated metadata or decorators. Using Config keeps the API simple and avoids conflicts. |
| **Field types** | ✅ StringField, IntField, etc. | ❌ Native Python types | pydantic_model uses native `str`, `int`, `float`, `bool` types with Pydantic's Field() for constraints. Custom field classes aren't needed since transforms/validators are Config-based. |
| **Computed fields** | ✅ Custom @computed_field | ✅ Use Pydantic's directly | utils/model has custom implementation; pydantic_model users directly use Pydantic's @computed_field decorator (no wrapper needed) |

### ❌ Unsupported Features (by Design)

| Feature | utils/model | utils/pydantic_model | Rationale |
|---------|-------------|----------------------|-----------|
| **StringField class** | ✅ | ❌ | Not needed - use native `str` type with Config-based transforms/validators |
| **IntField class** | ✅ | ❌ | Not needed - use native `int` type with Config-based transforms/validators |
| **FloatField class** | ✅ | ❌ | Not needed - use native `float` type with Config-based transforms/validators |
| **BoolField class** | ✅ | ❌ | Not needed - use native `bool` type with Config-based transforms/validators |
| **ListField class** | ✅ | ❌ | Not needed - use native `list[T]` with Pydantic's Field(min_length=, max_length=) |
| **DictField class** | ✅ | ❌ | Not needed - use native `dict[K, V]` with Pydantic validators |
| **ModelField class** | ✅ | ❌ | Not needed - Pydantic handles nested models automatically |
| **Field aliases** | ✅ Field(alias="name") | ✅ Pydantic Field(alias="name") | Supported but via Pydantic's Field(), not custom field classes |
| **Alias generator** | ✅ Config.alias_generator | ⚠️ Partial | Could be added via Pydantic's model_config, but not currently exposed in our Config wrapper |
| **exclude parameter** | ✅ Field(exclude=True) | ⚠️ Partial | Pydantic supports Field(exclude=True), but not exposed in our simplified API |
| **exclude_from_dict** | ✅ | ❌ | Pydantic has single exclude mechanism, not separate dict/json exclusions |
| **exclude_from_json** | ✅ | ❌ | Pydantic has single exclude mechanism, not separate dict/json exclusions |
| **item_type validation** | ✅ ListField(item_type=str) | ✅ list[str] | Supported via Python type hints, not field parameters |
| **item_validator** | ✅ ListField(item_validator=func) | ⚠️ Manual | Would need custom Pydantic validator decorator |
| **min_length/max_length** | ✅ ListField(min_length=1) | ✅ Field(min_length=1) | Supported via Pydantic's Field() constraints |
| **key_type/value_type** | ✅ DictField(key_type=str) | ✅ dict[str, int] | Supported via Python type hints |
| **value_validator** | ✅ DictField(value_validator=func) | ⚠️ Manual | Would need custom Pydantic validator decorator |

### ⚠️ Partially Supported / Could Add

These features exist in utils/model but aren't currently exposed in utils/pydantic_model. They could be added if needed:

| Feature | Status | How to Add |
|---------|--------|------------|
| **Alias generator** | Not exposed | Add to `__init_subclass__` to merge Pydantic's ConfigDict(alias_generator=...) |
| **Field(exclude=True)** | Not exposed | Document that users can use Pydantic's Field(exclude=True) directly |
| **exclude_from_dict vs exclude_from_json** | Not supported | Pydantic has unified exclude; separate mechanisms not available |
| **List item validators** | Manual workaround | Users can write custom @field_validator with Pydantic decorators |
| **Dict value validators** | Manual workaround | Users can write custom @field_validator with Pydantic decorators |

## API Comparison Examples

### Field-Level Transforms/Validators

**utils/model (supported):**
```python
from utils.model import Model, StringField
from utils import String, Validator

class User(Model):
    email: StringField = StringField(
        transform=[String.strip, String.lower],
        validate=Validator.email
    )
```

**utils/pydantic_model (NOT supported by design):**
```python
# ❌ Field-level transforms/validators don't work in pydantic_model
# This was attempted but conflicts with Pydantic v2 architecture

# ✅ Use Config-based approach instead:
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

### Field Types

**utils/model:**
```python
from utils.model import Model, StringField, IntField, ListField

class User(Model):
    name: StringField = StringField()
    age: IntField = IntField()
    tags: ListField = ListField(item_type=str, min_length=1)
```

**utils/pydantic_model:**
```python
from utils.pydantic_model import PydanticModel
from pydantic import Field

class User(PydanticModel):
    name: str
    age: int
    tags: list[str] = Field(min_length=1)
```

### Computed Fields

**utils/model:**
```python
from utils.model import Model, StringField, computed_field

class User(Model):
    first_name: StringField = StringField()
    last_name: StringField = StringField()

    @computed_field
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

**utils/pydantic_model:**
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
```

### Nested Models

**utils/model:**
```python
from utils.model import Model, StringField, ModelField

class Address(Model):
    street: StringField = StringField()
    city: StringField = StringField()

class User(Model):
    name: StringField = StringField()
    address: ModelField = ModelField(Address)
```

**utils/pydantic_model:**
```python
from utils.pydantic_model import PydanticModel

class Address(PydanticModel):
    street: str
    city: str

class User(PydanticModel):
    name: str
    address: Address  # Pydantic handles nested models automatically
```

## Design Rationale

### Why No Custom Field Classes?

During development, we attempted to create custom field classes (StringField, IntField, etc.) that would accept `transform` and `validate` parameters at the field level. However, we discovered:

1. **Pydantic v2 Architecture Conflict**: Pydantic v2 uses `Annotated` types and functional validators (`BeforeValidator`, `AfterValidator`), not `FieldInfo.metadata` for validation logic
2. **Descriptor Complexity**: Field-level transforms would require Python descriptors which conflict with Pydantic's internal property handling
3. **Maintenance Burden**: Custom field classes would require reimplementing much of Pydantic's validation infrastructure
4. **API Clarity**: Config-based transforms are more explicit and easier to understand

**Decision**: Use Config-based transforms/validators only, with native Python types. This keeps the implementation simple, leverages Pydantic's strengths, and avoids architectural conflicts.

### Why Config-Based Instead of Field-Level?

**Advantages of Config-based approach:**
- ✅ Works cleanly with Pydantic v2's validation system
- ✅ More explicit - all transforms/validators in one place
- ✅ Bulk operations are natural (already Config-based in utils/model)
- ✅ No conflicts with Pydantic's internal machinery
- ✅ Easier to maintain and extend

**Trade-offs:**
- ❌ Field-level transforms/validators are slightly more concise
- ❌ Requires migration from field-level to Config-based when moving from utils/model

### Why Delegate to Pydantic's computed_field?

utils/model has a custom `@computed_field` implementation, but Pydantic v2 has its own built-in `@computed_field` decorator that:
- Handles serialization automatically
- Supports property syntax
- Integrates with JSON schema generation
- Is well-tested and maintained

**Decision**: Use Pydantic's `@computed_field` directly rather than wrapping it.

### Why No Separate exclude_from_dict/exclude_from_json?

Pydantic v2 has a unified exclusion mechanism via `Field(exclude=True)` that applies to all serialization. Supporting separate dict vs JSON exclusions would require:
- Overriding Pydantic's serialization methods
- Custom tracking of per-method exclusions
- Potential conflicts with Pydantic's schema generation

**Decision**: Not worth the complexity for this edge case. Users can control exclusions per-call via `exclude_fields` parameter.

## Migration Guide: utils/model → utils/pydantic_model

### 1. Change Base Class
```python
# Before
from utils.model import Model

# After
from utils.pydantic_model import PydanticModel
```

### 2. Remove Custom Field Classes
```python
# Before
from utils.model import StringField, IntField

class User(Model):
    name: StringField = StringField()
    age: IntField = IntField()

# After
class User(PydanticModel):
    name: str
    age: int
```

### 3. Move Field-Level Transforms to Config
```python
# Before
class User(Model):
    email: StringField = StringField(
        transform=[str.strip, str.lower],
        validate=Validator.email
    )

# After
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

### 4. Use Pydantic Field for Constraints
```python
# Before
from utils.model import ListField

class User(Model):
    tags: ListField = ListField(item_type=str, min_length=1, max_length=10)

# After
from pydantic import Field

class User(PydanticModel):
    tags: list[str] = Field(min_length=1, max_length=10)
```

### 5. Update Computed Fields
```python
# Before
from utils.model import computed_field

class User(Model):
    first_name: StringField = StringField()
    last_name: StringField = StringField()

    @computed_field
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

# After
from pydantic import computed_field

class User(PydanticModel):
    first_name: str
    last_name: str

    @computed_field
    @property  # Note: Pydantic requires @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

### 6. Update Nested Models
```python
# Before
from utils.model import ModelField

class User(Model):
    address: ModelField = ModelField(Address)

# After
class User(PydanticModel):
    address: Address  # Pydantic auto-detects nested models
```

## When to Use Each Package

### Use utils/model when:
- ✅ You want zero Pydantic dependency
- ✅ Field-level transforms/validators are strongly preferred
- ✅ Working with existing utils/model codebases
- ✅ Building internal scripts/tools
- ✅ Fine-grained control over dict vs JSON exclusions is needed

### Use utils/pydantic_model when:
- ✅ You need Pydantic ecosystem integration (FastAPI, LangChain, etc.)
- ✅ Performance is critical (Pydantic v2 is 10-50x faster)
- ✅ JSON schema generation is required
- ✅ Better IDE support and type checking is desired
- ✅ Building production APIs
- ✅ Config-based transforms/validators are acceptable

## Summary

The `utils/pydantic_model` package preserves the core transform/validate API from `utils/model` while leveraging Pydantic v2's performance and ecosystem. The main architectural difference is Config-based (not field-level) transforms/validators, which aligns better with Pydantic v2's design and avoids conflicts with its internal machinery.

**Feature Parity: ~95%** - All core features are supported, with the only significant difference being the Config-based approach to transforms/validators instead of field-level.
