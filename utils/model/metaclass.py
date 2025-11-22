"""Metaclass for Model system."""

from __future__ import annotations

import types
from typing import Any, get_args, get_origin

from utils.model.fields import ComputedFieldDescriptor, Field
from utils.model.helpers import normalize_to_list


def is_optional_type(field_type: type) -> tuple[bool, type]:
    """Check if a type annotation is optional (Type | None).

    Returns:
        Tuple of (is_optional, actual_type)
    """
    origin = get_origin(field_type)
    if origin is types.UnionType:
        args = get_args(field_type)
        if type(None) in args:
            actual_type = next(arg for arg in args if arg is not type(None))
            return True, actual_type
    return False, field_type


def create_field_for_type(field_type: type) -> Field:
    """Create appropriate Field instance for a given type annotation."""
    from utils.model.fields import BoolField, FloatField, IntField, StringField

    type_to_field = {
        StringField: StringField,
        IntField: IntField,
        FloatField: FloatField,
        BoolField: BoolField,
    }
    field_class = type_to_field.get(field_type, Field)
    return field_class(required=False)


def process_field_annotation(
    field_name: str, field_type: type, namespace: dict
) -> tuple[Field, Any, bool] | None:
    """Process a single field annotation and return field metadata.

    Returns:
        Tuple of (field_instance, default, is_optional) or None if not a valid field
    """
    is_optional, actual_type = is_optional_type(field_type)
    field_instance = namespace.get(field_name)

    # Case 1: Explicit Field instance provided
    if isinstance(field_instance, Field):
        return (field_instance, field_instance.default, is_optional)

    # Case 2: Optional field with None value (auto-create Field)
    if field_instance is None and is_optional:
        field = create_field_for_type(actual_type)
        return (field, None, True)

    # Case 3: Not a valid field definition
    return None


def apply_bulk_transforms(
    fields: dict[str, tuple[Field, Any, bool]], apply_transforms: dict
) -> None:
    """Apply bulk transforms to multiple fields."""
    for field_names, transforms in apply_transforms.items():
        transform_list = normalize_to_list(transforms)
        for field_name in field_names:
            if field_name in fields:
                field_instance = fields[field_name][0]
                field_instance.transforms = transform_list + field_instance.transforms


def apply_bulk_validators(
    fields: dict[str, tuple[Field, Any, bool]], apply_validators: dict
) -> None:
    """Apply bulk validators to multiple fields."""
    for field_names, validators in apply_validators.items():
        validator_list = normalize_to_list(validators)
        for field_name in field_names:
            if field_name in fields:
                field_instance = fields[field_name][0]
                field_instance.validators = validator_list + field_instance.validators


class ModelMeta(type):
    """Metaclass for Model that processes field definitions."""

    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> type:
        """Create new Model class and process field annotations."""
        cls = super().__new__(mcs, name, bases, namespace)

        # Don't process the base Model class itself
        if name == "Model":
            return cls

        # Extract Config class if present
        config_class = namespace.get("Config")
        alias_generator = None
        apply_transforms_config = {}
        apply_validators_config = {}
        global_validators = []
        extra_fields_mode = "store"  # Default: store unknown fields
        json_serializer = None

        if config_class:
            alias_generator = getattr(config_class, "alias_generator", None)
            apply_transforms_config = getattr(config_class, "apply_transforms", {})
            apply_validators_config = getattr(config_class, "apply_validators", {})
            global_validators = getattr(config_class, "global_validators", [])
            extra_fields_mode = getattr(config_class, "extra_fields_mode", "store")
            json_serializer = getattr(config_class, "json_serializer", None)

        # Process all field annotations
        fields = mcs._collect_fields(namespace)

        # Apply bulk transforms and validators
        apply_bulk_transforms(fields, apply_transforms_config)
        apply_bulk_validators(fields, apply_validators_config)

        # Collect computed fields
        computed_fields = mcs._collect_computed_fields(namespace)

        # Store metadata on class
        cls._fields = fields
        cls._computed_fields = computed_fields
        cls._global_validators = global_validators
        cls._alias_generator = alias_generator
        cls._extra_fields_mode = extra_fields_mode
        cls._json_serializer = json_serializer

        # Set field descriptors as class attributes
        for field_name, (field_instance, _, _) in fields.items():
            # Manually call __set_name__ for auto-created fields
            if field_instance.name is None:
                field_instance.__set_name__(cls, field_name)
            setattr(cls, field_name, field_instance)

        return cls

    @staticmethod
    def _collect_fields(namespace: dict) -> dict[str, tuple[Field, Any, bool]]:
        """Collect and process all field annotations."""
        fields = {}
        annotations = namespace.get("__annotations__", {})

        for field_name, field_type in annotations.items():
            field_info = process_field_annotation(field_name, field_type, namespace)
            if field_info:
                fields[field_name] = field_info

        return fields

    @staticmethod
    def _collect_computed_fields(namespace: dict) -> dict[str, ComputedFieldDescriptor]:
        """Collect all computed field descriptors."""
        computed_fields = {}
        for name, value in namespace.items():
            if isinstance(value, ComputedFieldDescriptor):
                computed_fields[name] = value
        return computed_fields
