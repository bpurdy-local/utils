import threading
from typing import Any


class Beacon:
    """Global beacon for storing and retrieving application-wide values."""

    _storage: dict[str, Any] = {}
    _lock = threading.Lock()

    @staticmethod
    def _make_key(key: str, *, namespace: str | None = None) -> str:
        return f"{namespace}:{key}" if namespace else key

    @staticmethod
    def register(key: str, value: Any, *, namespace: str | None = None) -> None:
        """Register a value in the global beacon.

        Example: Beacon.register("api_key", "secret123", namespace="aws")
        """
        full_key = Beacon._make_key(key, namespace=namespace)
        with Beacon._lock:
            Beacon._storage[full_key] = value

    @staticmethod
    def get(key: str, *, namespace: str | None = None, default: Any = None, required: bool = False) -> Any:
        """Get a value from the beacon.

        Example: Beacon.get("api_key", namespace="aws", default="fallback")
        """
        full_key = Beacon._make_key(key, namespace=namespace)
        with Beacon._lock:
            if required and full_key not in Beacon._storage:
                raise KeyError(f"Beacon key '{full_key}' is required but not found")
            return Beacon._storage.get(full_key, default)

    @staticmethod
    def has(key: str, *, namespace: str | None = None) -> bool:
        """Check if a key exists in the beacon.

        Example: Beacon.has("api_key", namespace="aws")
        """
        full_key = Beacon._make_key(key, namespace=namespace)
        with Beacon._lock:
            return full_key in Beacon._storage

    @staticmethod
    def unregister(key: str, *, namespace: str | None = None) -> bool:
        """Remove a key from the beacon.

        Example: Beacon.unregister("api_key", namespace="aws")
        """
        full_key = Beacon._make_key(key, namespace=namespace)
        with Beacon._lock:
            if full_key in Beacon._storage:
                del Beacon._storage[full_key]
                return True
            return False

    @staticmethod
    def clear() -> None:
        """Clear all registered values.

        Example: Beacon.clear()
        """
        with Beacon._lock:
            Beacon._storage.clear()

    @staticmethod
    def list_keys(*, namespace: str | None = None) -> list[str]:
        """List all registered keys, optionally filtered by namespace.

        Example: Beacon.list_keys(namespace="aws")
        """
        with Beacon._lock:
            if namespace is None:
                return list(Beacon._storage.keys())
            prefix = f"{namespace}:"
            return [key for key in Beacon._storage.keys() if key.startswith(prefix)]

    @staticmethod
    def get_namespace(namespace: str) -> dict[str, Any]:
        """Get all values in a namespace.

        Example: Beacon.get_namespace("aws")
        """
        prefix = f"{namespace}:"
        with Beacon._lock:
            return {
                key[len(prefix):]: value
                for key, value in Beacon._storage.items()
                if key.startswith(prefix)
            }

    @staticmethod
    def clear_namespace(namespace: str) -> int:
        """Clear all keys in a namespace.

        Example: Beacon.clear_namespace("aws")
        """
        prefix = f"{namespace}:"
        with Beacon._lock:
            keys_to_delete = [key for key in Beacon._storage.keys() if key.startswith(prefix)]
            for key in keys_to_delete:
                del Beacon._storage[key]
            return len(keys_to_delete)
