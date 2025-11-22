"""Model system with field-based validation and transformation.

Provides a lightweight alternative to Pydantic with a cleaner API for defining
validated data models with automatic transforms and validation.

Example:
    ```python
    from utils import Model, StringField, IntField, Field
    from utils import String, Integer

    class User(Model):
        email: StringField = StringField(
            transform=[String.strip, String.lower],
            validate=Validator.is_email
        )
        age: IntField = IntField(
            validate=(Integer.clamp, min=0, max=120)
        )
        name: StringField | None = None  # Optional field
        role: StringField = StringField(default="user")  # With default

    # Automatic transform + validation on init
    user = User(email="  ADMIN@EXAMPLE.COM  ", age=25)
    # user.email -> "admin@example.com"

    # Re-validates on assignment
    user.age = 30  # OK
    user.age = 150  # Raises ValidationError

    # Dict conversion
    data = user.to_dict()  # or user.model_dump()
    user2 = User.from_dict(data)  # or User.model_validate(data)

    # Custom objects with proper typing
    class Address:
        def __init__(self, street, city):
            self.street = street
            self.city = city

    class Person(Model):
        name: StringField = StringField()
        address: Field[Address] = Field[Address]()  # Required custom object
        metadata: dict | None = None  # Optional with type inference
    ```
"""

from utils.model.exceptions import ValidationError
from utils.model.fields import (
    BoolField,
    DictField,
    Field,
    FloatField,
    IntField,
    ListField,
    ModelField,
    StringField,
    computed_field,
)
from utils.model.model import Model
from utils.model.serialization import to_camel

__all__ = [
    "Model",
    "Field",
    "StringField",
    "IntField",
    "FloatField",
    "BoolField",
    "ListField",
    "DictField",
    "ModelField",
    "ValidationError",
    "computed_field",
    "to_camel",
]
