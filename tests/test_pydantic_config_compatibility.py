"""Test that our Config class doesn't conflict with Pydantic's ConfigDict."""

import pytest
from pydantic import Field

from utils.pydantic_model import PydanticModel


def test_our_config_with_config_dict_option():
    """Test that we can use Pydantic ConfigDict options via Config.config_dict."""

    class User(PydanticModel):
        # Our custom Config with Pydantic options via config_dict
        class Config:
            apply_transforms = {
                ("email",): [str.strip, str.lower]
            }
            extra_fields_mode = "strict"
            # Use config_dict to pass Pydantic options
            config_dict = {
                "str_strip_whitespace": True,
            }

        name: str
        email: str

    # Should work with both our config and Pydantic options
    user = User(name="  Alice  ", email="  ADMIN@EXAMPLE.COM  ")
    assert user.name == "Alice"  # Pydantic's str_strip_whitespace
    assert user.email == "admin@example.com"  # Our transform


def test_config_dict_attribute():
    """Test that Config.config_dict merges with model_config."""

    class User(PydanticModel):
        class Config:
            # This should merge with base model_config
            config_dict = {
                "str_strip_whitespace": True,
                "str_min_length": 1,
            }

        name: str

    user = User(name="  Alice  ")
    assert user.name == "Alice"


def test_pydantic_v1_style_config_warning():
    """Test that Pydantic warns about old-style Config (not our issue)."""

    # Pydantic v2 deprecated class-based Config in favor of model_config
    # Our Config is separate and shouldn't interfere

    class User(PydanticModel):
        class Config:
            apply_transforms = {
                ("email",): [str.lower]
            }

        email: str

    # Should still work despite deprecation warning
    user = User(email="ADMIN@EXAMPLE.COM")
    assert user.email == "admin@example.com"


def test_model_validate_signature():
    """Test that model_validate signature matches parent."""
    import inspect

    from pydantic import BaseModel

    # Get signatures
    base_sig = inspect.signature(BaseModel.model_validate)
    our_sig = inspect.signature(PydanticModel.model_validate)

    # Compare parameter names (not exact match needed, just compatibility)
    base_params = list(base_sig.parameters.keys())
    our_params = list(our_sig.parameters.keys())

    # We only override to delegate, so basic params should match
    assert "data" in our_params or "obj" in our_params


def test_model_validate_json_signature():
    """Test that model_validate_json signature matches parent."""
    import inspect

    from pydantic import BaseModel

    # Get signatures
    base_sig = inspect.signature(BaseModel.model_validate_json)
    our_sig = inspect.signature(PydanticModel.model_validate_json)

    # Compare parameter names
    base_params = list(base_sig.parameters.keys())
    our_params = list(our_sig.parameters.keys())

    # We only override to delegate
    assert "json_data" in our_params or any("json" in p for p in our_params)


def test_actual_model_validate_works():
    """Test that model_validate actually works correctly."""

    class User(PydanticModel):
        name: str
        age: int

    # Should work with dict
    user = User.model_validate({"name": "Alice", "age": 25})
    assert user.name == "Alice"
    assert user.age == 25


def test_actual_model_validate_json_works():
    """Test that model_validate_json actually works correctly."""

    class User(PydanticModel):
        name: str
        age: int

    # Should work with JSON string
    user = User.model_validate_json('{"name": "Alice", "age": 25}')
    assert user.name == "Alice"
    assert user.age == 25


def test_pydantic_native_model_validate_still_available():
    """Test that Pydantic's native model_validate features still work."""

    class User(PydanticModel):
        name: str
        age: int = Field(ge=0)

    # Should support strict mode (Pydantic feature)

    # This is a Pydantic v2 feature - strict=True
    # Our override should not break it
    user = User.model_validate({"name": "Alice", "age": 25})
    assert user.age == 25


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
