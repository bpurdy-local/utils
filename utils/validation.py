"""Validation utility functions (backward compatibility wrappers)."""

from typing import Any

from utils.validator import Validator


def is_email(value: str) -> bool:
    """Check if string is a valid email (backward compatibility wrapper)."""
    return Validator.email(value)


def is_url(value: str) -> bool:
    """Check if string is a valid URL (backward compatibility wrapper)."""
    return Validator.url(value)


def is_phone(value: str) -> bool:
    """Check if string is a valid phone number (backward compatibility wrapper)."""
    return Validator.phone(value)


def is_credit_card(value: str) -> bool:
    """Check if string is a valid credit card (backward compatibility wrapper)."""
    return Validator.credit_card(value)


def is_uuid(value: str) -> bool:
    """Check if string is a valid UUID (backward compatibility wrapper)."""
    return Validator.uuid(value)


def is_hex_color(value: str) -> bool:
    """Check if string is a valid hex color (backward compatibility wrapper)."""
    return Validator.hex_color(value)


def is_ipv4(value: str) -> bool:
    """Check if string is a valid IPv4 (backward compatibility wrapper)."""
    return Validator.ipv4(value)


def is_empty(value: Any) -> bool:
    """Check if value is empty (backward compatibility wrapper)."""
    return Validator.empty(value)


def is_numeric(value: str) -> bool:
    """Check if string is numeric (backward compatibility wrapper)."""
    return Validator.numeric(value)


def is_integer(value: str) -> bool:
    """Check if string is an integer (backward compatibility wrapper)."""
    return Validator.integer(value)
