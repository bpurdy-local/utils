from collections.abc import Callable
from typing import Any


class Dict:
    """Static utility class for dictionary operations."""

    @staticmethod
    def pick(d: dict[str, Any], *keys: str) -> dict[str, Any]:
        """Include only specified keys from dictionary.

        Examples:
            >>> Dict.pick({'a': 1, 'b': 2, 'c': 3}, 'a', 'c')
            {'a': 1, 'c': 3}
        """
        # Include only specified keys
        return {k: v for k, v in d.items() if k in keys}

    @staticmethod
    def omit(d: dict[str, Any], *keys: str) -> dict[str, Any]:
        """Exclude specified keys from dictionary.

        Examples:
            >>> Dict.omit({'a': 1, 'b': 2, 'c': 3}, 'b')
            {'a': 1, 'c': 3}
        """
        # Exclude specified keys
        return {k: v for k, v in d.items() if k not in keys}

    @staticmethod
    def deep_get(d: dict[str, Any], *, path: str, default: Any = None) -> Any:
        """Get value from nested dictionary using dot-separated path.

        Examples:
            >>> Dict.deep_get({'a': {'b': {'c': 42}}}, path='a.b.c')
            42
        """
        # Traverse nested dicts using dot-separated path (e.g., "a.b.c")
        keys = path.split(".")
        current = d
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    @staticmethod
    def deep_set(d: dict[str, Any], *, path: str, value: Any) -> None:
        """Set value in nested dictionary using dot-separated path.

        Examples:
            >>> d = {}
            >>> Dict.deep_set(d, path='user.profile.name', value='Alice')
            >>> d
            {'user': {'profile': {'name': 'Alice'}}}
        """
        # Create nested dicts as needed along the path
        keys = path.split(".")
        current = d
        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    @staticmethod
    def merge(d: dict[str, Any], *, other: dict[str, Any], deep: bool = False) -> dict[str, Any]:
        """Merge two dictionaries, optionally performing deep merge.

        Examples:
            >>> Dict.merge({'a': 1, 'b': 2}, other={'b': 3, 'c': 4})
            {'a': 1, 'b': 3, 'c': 4}

            >>> Dict.merge({'a': {'b': 1}}, other={'a': {'c': 2}}, deep=True)
            {'a': {'b': 1, 'c': 2}}
        """
        if not deep:
            return {**d, **other}

        # Recursively merge nested dicts when both values are dicts
        result = d.copy()
        for key, value in other.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Dict.merge(result[key], other=value, deep=True)
            else:
                result[key] = value
        return result

    @staticmethod
    def invert(d: dict[str, Any]) -> dict[str, Any]:
        """Swap keys and values in dictionary.

        Examples:
            >>> Dict.invert({'a': 1, 'b': 2})
            {1: 'a', 2: 'b'}
        """
        # Swap keys and values (e.g., {"a": 1} -> {1: "a"})
        return {v: k for k, v in d.items()}

    @staticmethod
    def map_values(d: dict[str, Any], *, func: Callable[[Any], Any]) -> dict[str, Any]:
        """Transform all values in dictionary using function.

        Examples:
            >>> Dict.map_values({'a': 1, 'b': 2}, func=lambda x: x * 2)
            {'a': 2, 'b': 4}
        """
        # Transform all values using function
        return {k: func(v) for k, v in d.items()}

    @staticmethod
    def map_keys(d: dict[str, Any], *, func: Callable[[str], str]) -> dict[str, Any]:
        """Transform all keys in dictionary using function.

        Examples:
            >>> Dict.map_keys({'a': 1, 'b': 2}, func=str.upper)
            {'A': 1, 'B': 2}
        """
        # Transform all keys using function
        return {func(k): v for k, v in d.items()}

    @staticmethod
    def filter(d: dict[str, Any], *, predicate: Callable[[str, Any], bool]) -> dict[str, Any]:
        """Filter dictionary keeping only entries matching predicate.

        Examples:
            >>> Dict.filter({'a': 1, 'b': 2, 'c': 3}, predicate=lambda k, v: v > 1)
            {'b': 2, 'c': 3}
        """
        # Keep only key-value pairs that match predicate
        return {k: v for k, v in d.items() if predicate(k, v)}

    @staticmethod
    def defaults(d: dict[str, Any], *, defaults: dict[str, Any]) -> dict[str, Any]:
        """Add default values for missing keys in dictionary.

        Examples:
            >>> Dict.defaults({'a': 1}, defaults={'b': 2, 'c': 3})
            {'a': 1, 'b': 2, 'c': 3}

            >>> Dict.defaults({'a': 1, 'b': 2}, defaults={'b': 99})
            {'a': 1, 'b': 2}
        """
        # Add default values for missing keys
        result = d.copy()
        for key, value in defaults.items():
            if key not in result:
                result[key] = value
        return result

    @staticmethod
    def compact(d: dict[str, Any]) -> dict[str, Any]:
        """Remove all None values from dictionary.

        Examples:
            >>> Dict.compact({'a': 1, 'b': None, 'c': 3})
            {'a': 1, 'c': 3}
        """
        # Remove all None values
        return {k: v for k, v in d.items() if v is not None}

    @staticmethod
    def flatten(d: dict[str, Any], *, separator: str = ".") -> dict[str, Any]:
        """Flatten nested dictionary into single-level with compound keys.

        Examples:
            >>> Dict.flatten({'a': {'b': {'c': 1}}})
            {'a.b.c': 1}
        """

        # Convert nested dicts to flat dict with compound keys (e.g., {"a": {"b": 1}} -> {"a.b": 1})
        def _flatten(obj: Any, parent_key: str = "") -> dict[str, Any]:
            items = []
            for k, v in obj.items():
                new_key = f"{parent_key}{separator}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(_flatten(v, new_key).items())
                else:
                    items.append((new_key, v))
            return dict(items)

        return _flatten(d)

    @staticmethod
    def unflatten(d: dict[str, Any], *, separator: str = ".") -> dict[str, Any]:
        """Reconstruct nested dictionary from flattened compound keys.

        Examples:
            >>> Dict.unflatten({'a.b.c': 1})
            {'a': {'b': {'c': 1}}}
        """
        # Reconstruct nested dicts from flat keys (e.g., {"a.b": 1} -> {"a": {"b": 1}})
        result: dict[str, Any] = {}
        for key, value in d.items():
            keys = key.split(separator)
            current = result
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
        return result
