"""Type conversion and parsing utilities."""

import re
from typing import Any, TypeVar

T = TypeVar("T")


class Convert:
    """Static utility class for type conversions and parsing."""

    # Boolean conversion mappings
    _TRUE_VALUES = {"true", "yes", "y", "1", "on", "t", "enabled", "enable"}
    _FALSE_VALUES = {"false", "no", "n", "0", "off", "f", "disabled", "disable"}

    # Duration pattern: "2h 30m 15s" or "2h30m15s" or combinations
    _DURATION_PATTERN = re.compile(r"(?:(\d+(?:\.\d+)?)\s*([dhms]))", re.IGNORECASE)

    # Byte size pattern: "1.5GB", "500MB", "2KB", etc.
    _BYTES_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)\s*([KMGT]?B)?$", re.IGNORECASE)

    @staticmethod
    def to_bool(value: Any, *, default: bool | None = None) -> bool | None:
        """Convert value to boolean with smart parsing.

        Recognizes: true/false, yes/no, y/n, 1/0, on/off, t/f, enabled/disabled

        Examples:
            >>> Convert.to_bool("true")
            True
            >>> Convert.to_bool("yes")
            True
            >>> Convert.to_bool("1")
            True
            >>> Convert.to_bool("off")
            False
            >>> Convert.to_bool("invalid", default=False)
            False
            >>> Convert.to_bool(1)
            True
            >>> Convert.to_bool(0)
            False
        """
        # Handle native bool
        if isinstance(value, bool):
            return value

        # Handle int/float
        if isinstance(value, (int, float)):
            return bool(value)

        # Handle None
        if value is None:
            return default

        # Handle string
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in Convert._TRUE_VALUES:
                return True
            if normalized in Convert._FALSE_VALUES:
                return False

        return default

    @staticmethod
    def _clean_numeric_string(value: str) -> str:
        """Internal helper to clean numeric strings (remove commas, whitespace)."""
        return value.replace(",", "").strip()

    @staticmethod
    def to_int(value: Any, *, default: int | None = None) -> int | None:
        """Convert value to integer with safe parsing.

        Handles: strings with commas, floats, booleans

        Examples:
            >>> Convert.to_int("123")
            123
            >>> Convert.to_int("1,234")
            1234
            >>> Convert.to_int("1,234.56")
            1234
            >>> Convert.to_int(12.8)
            12
            >>> Convert.to_int(True)
            1
            >>> Convert.to_int("invalid", default=0)
            0
        """
        if isinstance(value, int):
            return value

        if isinstance(value, bool):
            return int(value)

        if isinstance(value, float):
            return int(value)

        if isinstance(value, str):
            cleaned = Convert._clean_numeric_string(value)
            try:
                # Try parsing as float first (handles decimals)
                return int(float(cleaned))
            except (ValueError, TypeError):
                return default

        return default

    @staticmethod
    def to_float(value: Any, *, default: float | None = None) -> float | None:
        """Convert value to float with safe parsing.

        Handles: strings with commas, integers, booleans

        Examples:
            >>> Convert.to_float("123.45")
            123.45
            >>> Convert.to_float("1,234.56")
            1234.56
            >>> Convert.to_float(123)
            123.0
            >>> Convert.to_float(True)
            1.0
            >>> Convert.to_float("invalid", default=0.0)
            0.0
        """
        if isinstance(value, float):
            return value

        if isinstance(value, bool):
            return float(value)

        if isinstance(value, int):
            return float(value)

        if isinstance(value, str):
            cleaned = Convert._clean_numeric_string(value)
            try:
                return float(cleaned)
            except (ValueError, TypeError):
                return default

        return default

    @staticmethod
    def to_str(value: Any, *, default: str = "") -> str:
        """Convert value to string with safe handling.

        Examples:
            >>> Convert.to_str(123)
            '123'
            >>> Convert.to_str(None)
            ''
            >>> Convert.to_str(None, default="N/A")
            'N/A'
            >>> Convert.to_str([1, 2, 3])
            '[1, 2, 3]'
        """
        if value is None:
            return default
        return str(value)

    @staticmethod
    def to_number(value: Any, *, default: int | float | None = None) -> int | float | None:
        """Convert to int if possible, otherwise float, with safe parsing.

        Examples:
            >>> Convert.to_number("123")
            123
            >>> Convert.to_number("123.45")
            123.45
            >>> Convert.to_number("1,234")
            1234
            >>> Convert.to_number("1,234.56")
            1234.56
            >>> Convert.to_number("invalid", default=0)
            0
        """
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return value

        if isinstance(value, str):
            cleaned = Convert._clean_numeric_string(value)
            try:
                # Try int first
                if "." not in cleaned:
                    return int(cleaned)
                # Try float
                float_val = float(cleaned)
                # If it's a whole number, return as int
                if float_val.is_integer():
                    return int(float_val)
                return float_val
            except (ValueError, TypeError):
                return default

        return default

    @staticmethod
    def bytes_from_human(size_str: str, *, default: int | None = None) -> int | None:
        """Convert human-readable byte size to integer bytes.

        Supports: B, KB, MB, GB, TB (case-insensitive)

        Examples:
            >>> Convert.bytes_from_human("1KB")
            1024
            >>> Convert.bytes_from_human("1.5GB")
            1610612736
            >>> Convert.bytes_from_human("500MB")
            524288000
            >>> Convert.bytes_from_human("2 TB")
            2199023255552
            >>> Convert.bytes_from_human("invalid", default=0)
            0
        """
        if not isinstance(size_str, str):
            return default

        match = Convert._BYTES_PATTERN.match(size_str.strip())
        if not match:
            return default

        try:
            value = float(match.group(1))
            unit = (match.group(2) or "B").upper()

            multipliers = {
                "B": 1,
                "KB": 1024,
                "MB": 1024**2,
                "GB": 1024**3,
                "TB": 1024**4,
            }

            return int(value * multipliers.get(unit, 1))
        except (ValueError, TypeError):
            return default

    @staticmethod
    def duration(duration_str: str, *, default: int | None = None) -> int | None:
        """Convert duration string to seconds.

        Supports: d (days), h (hours), m (minutes), s (seconds)

        Examples:
            >>> Convert.duration("2h")
            7200
            >>> Convert.duration("30m")
            1800
            >>> Convert.duration("2h 30m")
            9000
            >>> Convert.duration("1d 2h 30m 15s")
            95415
            >>> Convert.duration("2.5h")
            9000
            >>> Convert.duration("invalid", default=0)
            0
        """
        if not isinstance(duration_str, str):
            return default

        matches = Convert._DURATION_PATTERN.findall(duration_str)
        if not matches:
            return default

        try:
            total_seconds = 0
            for value_str, unit in matches:
                value = float(value_str)
                unit_lower = unit.lower()

                if unit_lower == "d":
                    total_seconds += value * 86400
                elif unit_lower == "h":
                    total_seconds += value * 3600
                elif unit_lower == "m":
                    total_seconds += value * 60
                elif unit_lower == "s":
                    total_seconds += value

            return int(total_seconds)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def safe_cast(value: Any, target_type: type[T], *, default: T | None = None) -> T | None:
        """Safely cast value to target type with fallback.

        Examples:
            >>> Convert.safe_cast("123", int)
            123
            >>> Convert.safe_cast("123.45", float)
            123.45
            >>> Convert.safe_cast("invalid", int, default=0)
            0
            >>> Convert.safe_cast("true", bool)
            True
            >>> Convert.safe_cast([1, 2, 3], list)
            [1, 2, 3]
        """
        # Already the target type
        if isinstance(value, target_type):
            return value

        # Special handling for bool (to avoid int/float converting to bool)
        if target_type is bool:
            result = Convert.to_bool(value, default=default)
            return result if result is not None else default

        # Special handling for str
        if target_type is str:
            return Convert.to_str(value, default=default or "")

        # Try direct conversion for basic types
        try:
            if target_type in (int, float, str, bool, list, tuple, set, dict):
                return target_type(value)
        except (ValueError, TypeError):
            return default

        # Fallback
        return default

    @staticmethod
    def to_list(value: Any, *, separator: str = ",", default: list | None = None) -> list:
        """Convert value to list.

        For strings, splits by separator. For single values, wraps in list.

        Examples:
            >>> Convert.to_list("a,b,c")
            ['a', 'b', 'c']
            >>> Convert.to_list("a, b, c")
            ['a', 'b', 'c']
            >>> Convert.to_list("a")
            ['a']
            >>> Convert.to_list([1, 2, 3])
            [1, 2, 3]
            >>> Convert.to_list((1, 2, 3))
            [1, 2, 3]
            >>> Convert.to_list(None, default=[])
            []
        """
        if default is None:
            default = []

        if value is None:
            return default

        if isinstance(value, list):
            return value

        if isinstance(value, (tuple, set)):
            return list(value)

        if isinstance(value, str):
            # Split and strip whitespace
            return [item.strip() for item in value.split(separator) if item.strip()]

        # Single value - wrap in list
        return [value]

    @staticmethod
    def to_dict(value: Any, *, default: dict | None = None) -> dict:
        """Convert value to dictionary if possible.

        Examples:
            >>> Convert.to_dict({"a": 1})
            {'a': 1}
            >>> Convert.to_dict([("a", 1), ("b", 2)])
            {'a': 1, 'b': 2}
            >>> Convert.to_dict(None, default={})
            {}
        """
        if default is None:
            default = {}

        if value is None:
            return default

        if isinstance(value, dict):
            return value

        # Try converting from list of tuples or similar
        try:
            return dict(value)
        except (ValueError, TypeError):
            return default
