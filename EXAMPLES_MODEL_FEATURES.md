# Model System - New Features Examples

This document showcases the 5 major features added to the Model system.

## 1. Better Error Messages

ValidationError now includes detailed field-level errors:

```python
from utils import Model, IntField, StringField, ValidationError

class User(Model):
    name: StringField = StringField()
    age: IntField = IntField(validate=lambda x: x >= 18)
    email: StringField = StringField()

try:
    user = User(name="Alice", age=15, email="invalid")
except ValidationError as e:
    print(str(e))
    # Validation failed for field 'age' with value: 15

    # Access structured errors
    if e.errors:
        for error in e.errors:
            print(f"{error['field']}: {error['message']}")
```

## 2. Field Exclusion

Control which fields appear in dict/JSON serialization:

```python
from utils import Model, StringField

class User(Model):
    username: StringField = StringField()
    password: StringField = StringField(exclude=True)  # Never serialized
    internal_id: StringField = StringField(exclude_from_json=True)  # Only excluded from JSON
    display_name: StringField = StringField(exclude_from_dict=True)  # Only excluded from dict

user = User(
    username="alice",
    password="secret123",
    internal_id="UUID-1234",
    display_name="Alice"
)

print(user.to_dict())
# {'username': 'alice', 'display_name': 'Alice'}
# (password is excluded, internal_id is in dict)

print(user.json())
# {"username": "alice"}
# (password and internal_id excluded, display_name is in JSON)

# Exclude None values
user2 = User(username="bob", password="pass", internal_id="UUID-5678", display_name=None)
print(user2.to_dict(exclude_none=True))
# {'username': 'bob', 'internal_id': 'UUID-5678'}
```

## 3. Field Aliases

Use different names for serialization vs Python attributes:

```python
from utils import Model, StringField, IntField

class APIResponse(Model):
    user_id: IntField = IntField(alias="userId")  # API uses camelCase
    email_address: StringField = StringField(alias="emailAddress")
    full_name: StringField = StringField(alias="fullName")

# Create from API response (with aliases)
api_data = {
    "userId": 123,
    "emailAddress": "alice@example.com",
    "fullName": "Alice Smith"
}
response = APIResponse.from_dict(api_data)

# Access with Python naming
print(response.user_id)  # 123
print(response.email_address)  # alice@example.com

# Serialize back to API format (with aliases)
print(response.to_dict())
# {'userId': 123, 'emailAddress': 'alice@example.com', 'fullName': 'Alice Smith'}
```

## 4. List/Dict Field Types

Typed collections with automatic validation:

```python
from utils import Model, StringField, IntField, ListField, DictField

# List with type validation
class Team(Model):
    name: StringField = StringField()
    members: ListField = ListField(
        item_type=str,
        min_length=1,
        max_length=10
    )
    scores: ListField = ListField(
        item_type=int,
        item_validator=lambda x: x >= 0 and x <= 100
    )

team = Team(
    name="Alpha",
    members=["Alice", "Bob", "Charlie"],
    scores=[95, 87, 92]
)

# Dict with type validation
class Config(Model):
    app_name: StringField = StringField()
    settings: DictField = DictField(
        key_type=str,
        value_type=int
    )
    features: DictField = DictField(
        value_validator=lambda x: isinstance(x, bool)
    )

config = Config(
    app_name="MyApp",
    settings={"timeout": 30, "retries": 3},
    features={"darkMode": True, "notifications": False}
)
```

## 5. Nested Model Validation

Automatic conversion of dicts to Model instances:

```python
from utils import Model, StringField, IntField, ModelField, ListField, DictField

# Define nested models
class Address(Model):
    street: StringField = StringField()
    city: StringField = StringField()
    zipcode: StringField = StringField()

class Person(Model):
    name: StringField = StringField()
    age: IntField = IntField()
    address: ModelField[Address] = ModelField(Address)

# Create from nested dict - Address is automatically created
person = Person.from_dict({
    "name": "Alice",
    "age": 30,
    "address": {
        "street": "123 Main St",
        "city": "NYC",
        "zipcode": "10001"
    }
})

print(person.address.city)  # NYC
print(type(person.address))  # <class 'Address'>

# Works with ListField too!
class Company(Model):
    name: StringField = StringField()
    employees: ListField = ListField(item_type=Person)

company = Company.from_dict({
    "name": "TechCorp",
    "employees": [
        {
            "name": "Alice",
            "age": 30,
            "address": {"street": "123 Main", "city": "NYC", "zipcode": "10001"}
        },
        {
            "name": "Bob",
            "age": 25,
            "address": {"street": "456 Oak", "city": "LA", "zipcode": "90001"}
        }
    ]
})

print(len(company.employees))  # 2
print(company.employees[0].name)  # Alice
print(company.employees[1].address.city)  # LA

# Works with DictField too!
class Organization(Model):
    name: StringField = StringField()
    departments: DictField = DictField(value_type=Person)

org = Organization.from_dict({
    "name": "ACME",
    "departments": {
        "engineering": {
            "name": "Alice",
            "age": 30,
            "address": {"street": "123 Main", "city": "NYC", "zipcode": "10001"}
        },
        "sales": {
            "name": "Bob",
            "age": 25,
            "address": {"street": "456 Oak", "city": "LA", "zipcode": "90001"}
        }
    }
})

print(org.departments["engineering"].name)  # Alice
print(org.departments["sales"].address.city)  # LA
```

## Complete Example: API Integration

Here's a real-world example combining all features:

```python
from utils import Model, StringField, IntField, ListField, ModelField, ValidationError

class Tag(Model):
    name: StringField = StringField()
    color: StringField = StringField()

class Post(Model):
    post_id: IntField = IntField(alias="postId")
    title: StringField = StringField()
    content: StringField = StringField()
    author_id: IntField = IntField(alias="authorId")
    tags: ListField = ListField(item_type=Tag, max_length=5)
    metadata: dict | None = None

    # Internal fields not sent to API
    internal_notes: StringField | None = StringField(exclude=True, default=None)

# Parse API response
api_response = {
    "postId": 42,
    "title": "Introduction to Models",
    "content": "This is a great post...",
    "authorId": 123,
    "tags": [
        {"name": "python", "color": "blue"},
        {"name": "tutorial", "color": "green"}
    ],
    "metadata": {"views": 1500, "likes": 42}
}

post = Post.from_dict(api_response)

# Access with Python naming
print(post.post_id)  # 42
print(post.tags[0].name)  # python

# Add internal notes (won't be serialized)
post.internal_notes = "Review this later"

# Serialize back to API format
print(post.json(exclude_none=True, indent=2))
# {
#   "postId": 42,
#   "title": "Introduction to Models",
#   "content": "This is a great post...",
#   "authorId": 123,
#   "tags": [
#     {"name": "python", "color": "blue"},
#     {"name": "tutorial", "color": "green"}
#   ],
#   "metadata": {"views": 1500, "likes": 42}
# }
# Note: internal_notes is excluded, metadata is included
```

## Error Handling

The improved error messages make debugging much easier:

```python
from utils import Model, IntField, ListField, ValidationError

class Config(Model):
    timeout: IntField = IntField(validate=lambda x: x > 0)
    ports: ListField = ListField(
        item_type=int,
        min_length=1,
        item_validator=lambda x: x >= 1024 and x <= 65535
    )

try:
    config = Config(
        timeout=-5,
        ports=[80, 443, 99999]
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
    # Shows which field and what value caused the error
```

All features work together seamlessly to provide a powerful, type-safe model system!
