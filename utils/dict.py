from collections.abc import Callable
from typing import Any


class Dict:
    @staticmethod
    def pick(d: dict[str, Any], *keys: str) -> dict[str, Any]:
        return {k: v for k, v in d.items() if k in keys}

    @staticmethod
    def omit(d: dict[str, Any], *keys: str) -> dict[str, Any]:
        return {k: v for k, v in d.items() if k not in keys}

    @staticmethod
    def deep_get(d: dict[str, Any], *, path: str, default: Any = None) -> Any:
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
        keys = path.split(".")
        current = d
        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    @staticmethod
    def merge(d: dict[str, Any], *, other: dict[str, Any], deep: bool = False) -> dict[str, Any]:
        if not deep:
            return {**d, **other}

        result = d.copy()
        for key, value in other.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Dict.merge(result[key], other=value, deep=True)
            else:
                result[key] = value
        return result

    @staticmethod
    def invert(d: dict[str, Any]) -> dict[str, Any]:
        return {v: k for k, v in d.items()}

    @staticmethod
    def map_values(d: dict[str, Any], *, func: Callable[[Any], Any]) -> dict[str, Any]:
        return {k: func(v) for k, v in d.items()}

    @staticmethod
    def map_keys(d: dict[str, Any], *, func: Callable[[str], str]) -> dict[str, Any]:
        return {func(k): v for k, v in d.items()}

    @staticmethod
    def filter(d: dict[str, Any], *, predicate: Callable[[str, Any], bool]) -> dict[str, Any]:
        return {k: v for k, v in d.items() if predicate(k, v)}

    @staticmethod
    def defaults(d: dict[str, Any], *, defaults: dict[str, Any]) -> dict[str, Any]:
        result = d.copy()
        for key, value in defaults.items():
            if key not in result:
                result[key] = value
        return result

    @staticmethod
    def compact(d: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in d.items() if v is not None}

    @staticmethod
    def flatten(d: dict[str, Any], *, separator: str = ".") -> dict[str, Any]:
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
