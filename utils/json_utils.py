"""JSON utility class."""

import json
from typing import Any


class JSON:
    """Static utility class for advanced JSON operations."""

    @staticmethod
    def pretty(data: Any, *, indent: int = 2) -> str:
        """Pretty print JSON with indentation.

        Examples:
            >>> JSON.pretty({"a": 1, "b": 2})
            '{\\n  "a": 1,\\n  "b": 2\\n}'
            >>> JSON.pretty([1, 2, 3], indent=4)
            '[\\n    1,\\n    2,\\n    3\\n]'
        """
        return json.dumps(data, indent=indent, ensure_ascii=False)

    @staticmethod
    def minify(json_str: str) -> str:
        """Minify JSON string by removing whitespace.

        Examples:
            >>> JSON.minify('{"a": 1, "b": 2}')
            '{"a":1,"b":2}'
        """
        # Parse and re-dump with minimal separators
        data = json.loads(json_str)
        return json.dumps(data, separators=(",", ":"), ensure_ascii=False)

    @staticmethod
    def flatten(data: dict, *, separator: str = ".") -> dict[str, Any]:
        """Flatten nested dictionary to dot notation.

        Examples:
            >>> JSON.flatten({"a": {"b": 1, "c": 2}})
            {'a.b': 1, 'a.c': 2}
            >>> JSON.flatten({"x": {"y": {"z": 3}}})
            {'x.y.z': 3}
            >>> JSON.flatten({"a": 1, "b": 2})
            {'a': 1, 'b': 2}
        """
        result = {}

        def _flatten(obj: Any, prefix: str = "") -> None:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{prefix}{separator}{key}" if prefix else key
                    if isinstance(value, dict) and value:  # Only recurse non-empty dicts
                        _flatten(value, new_key)
                    else:
                        result[new_key] = value
            else:
                result[prefix] = obj

        _flatten(data)
        return result

    @staticmethod
    def unflatten(data: dict, *, separator: str = ".") -> dict[str, Any]:
        """Unflatten dot notation dictionary to nested structure.

        Examples:
            >>> JSON.unflatten({"a.b": 1, "a.c": 2})
            {'a': {'b': 1, 'c': 2}}
            >>> JSON.unflatten({"x.y.z": 3})
            {'x': {'y': {'z': 3}}}
        """
        result: dict[str, Any] = {}

        for key, value in data.items():
            parts = key.split(separator)
            current = result

            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            current[parts[-1]] = value

        return result

    @staticmethod
    def parse(json_str: str, *, default: Any = None) -> Any:
        """Safe JSON parsing that returns default on error.

        Examples:
            >>> JSON.parse('{"a": 1}')
            {'a': 1}
            >>> JSON.parse('invalid json', default={})
            {}
            >>> JSON.parse('invalid', default=None)
        """
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError, ValueError):
            return default

    @staticmethod
    def validate_schema(data: Any, schema: dict) -> bool:
        """Basic schema validation (type checking only).

        Schema format: {"field": type, "nested.field": type}
        Supported types: str, int, float, bool, list, dict

        Examples:
            >>> schema = {"name": str, "age": int}
            >>> JSON.validate_schema({"name": "John", "age": 30}, schema)
            True
            >>> JSON.validate_schema({"name": "John", "age": "30"}, schema)
            False
        """
        for field, expected_type in schema.items():
            # Navigate to the field value
            keys = field.split(".")
            current = data

            try:
                for key in keys:
                    current = current[key]
            except (KeyError, TypeError):
                return False

            # Check if type matches
            if not isinstance(current, expected_type):
                return False

        return True

    @staticmethod
    def to_string(data: Any, *, pretty: bool = False, indent: int = 2) -> str:
        """Convert data to JSON string.

        Examples:
            >>> JSON.to_string({"a": 1})
            '{"a": 1}'
            >>> result = JSON.to_string({"a": 1}, pretty=True)
            >>> "\\n" in result
            True
        """
        if pretty:
            return JSON.pretty(data, indent=indent)
        return json.dumps(data, ensure_ascii=False)

    @staticmethod
    def from_string(json_str: str) -> Any:
        """Parse JSON string to Python object.

        Examples:
            >>> JSON.from_string('{"a": 1}')
            {'a': 1}
        """
        return json.loads(json_str)

    @staticmethod
    def is_valid(json_str: str) -> bool:
        """Check if string is valid JSON.

        Examples:
            >>> JSON.is_valid('{"a": 1}')
            True
            >>> JSON.is_valid('invalid')
            False
        """
        try:
            json.loads(json_str)
            return True
        except (json.JSONDecodeError, TypeError, ValueError):
            return False
