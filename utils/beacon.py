import threading
import time
from datetime import timedelta
from typing import Any


class Beacon:
    """Global beacon for storing and retrieving application-wide values with optional TTL."""

    _storage: dict[str, tuple[Any, float | None]] = {}
    _lock = threading.Lock()
    _stats = {"hits": 0, "misses": 0}

    @staticmethod
    def _make_key(key: str, *, namespace: str | None = None) -> str:
        return f"{namespace}:{key}" if namespace else key

    @staticmethod
    def _is_expired(expiry: float | None) -> bool:
        """Check if entry has expired."""
        if expiry is None:
            return False
        return time.time() > expiry

    @staticmethod
    def _auto_cleanup_expired() -> None:
        """Internal method to automatically clean up expired entries (called during register)."""
        current_time = time.time()
        keys_to_delete = []

        for key, (_, expiry) in Beacon._storage.items():
            if expiry is not None and current_time > expiry:
                keys_to_delete.append(key)

        for key in keys_to_delete:
            del Beacon._storage[key]

    @staticmethod
    def register(
        key: str,
        value: Any,
        *,
        namespace: str | None = None,
        ttl: int | timedelta | None = None,
    ) -> None:
        """Register a value in the global beacon with optional TTL.

        Automatically cleans up expired entries during registration.

        Args:
            key: The key to register
            value: The value to store
            namespace: Optional namespace to organize keys
            ttl: Time-to-live in seconds (int) or as timedelta (None for permanent)

        Examples:
            >>> Beacon.register("api_key", "secret123", namespace="aws")
            >>> Beacon.register("temp_token", "xyz", ttl=60)  # 60 seconds
            >>> from datetime import timedelta
            >>> Beacon.register("cache", data, ttl=timedelta(hours=1))
            >>> Beacon.register("session", user_data, ttl=timedelta(days=7))
        """
        full_key = Beacon._make_key(key, namespace=namespace)

        # Convert timedelta to seconds if needed
        if isinstance(ttl, timedelta):
            ttl_seconds = ttl.total_seconds()
        else:
            ttl_seconds = ttl

        expiry = time.time() + ttl_seconds if ttl_seconds is not None else None

        with Beacon._lock:
            # Auto-cleanup expired entries on every write
            Beacon._auto_cleanup_expired()
            Beacon._storage[full_key] = (value, expiry)

    @staticmethod
    def get(
        key: str, *, namespace: str | None = None, default: Any = None, required: bool = False
    ) -> Any:
        """Get a value from the beacon, returning default if not found or expired.

        Examples:
            >>> Beacon.register("api_key", "secret123", namespace="aws")
            >>> Beacon.get("api_key", namespace="aws", default="fallback")
            'secret123'
        """
        full_key = Beacon._make_key(key, namespace=namespace)

        with Beacon._lock:
            if full_key not in Beacon._storage:
                Beacon._stats["misses"] += 1
                if required:
                    raise KeyError(f"Beacon key '{full_key}' is required but not found")
                return default

            value, expiry = Beacon._storage[full_key]

            # Check if expired
            if Beacon._is_expired(expiry):
                del Beacon._storage[full_key]
                Beacon._stats["misses"] += 1
                if required:
                    raise KeyError(f"Beacon key '{full_key}' is required but not found")
                return default

            Beacon._stats["hits"] += 1
            return value

    @staticmethod
    def has(key: str, *, namespace: str | None = None) -> bool:
        """Check if a key exists and is not expired.

        Examples:
            >>> Beacon.register("api_key", "secret123", namespace="aws")
            >>> Beacon.has("api_key", namespace="aws")
            True
        """
        full_key = Beacon._make_key(key, namespace=namespace)

        with Beacon._lock:
            if full_key not in Beacon._storage:
                return False

            _, expiry = Beacon._storage[full_key]
            if Beacon._is_expired(expiry):
                del Beacon._storage[full_key]
                return False

            return True

    @staticmethod
    def unregister(key: str, *, namespace: str | None = None) -> bool:
        """Remove a key from the beacon.

        Examples:
            >>> Beacon.register("api_key", "secret123", namespace="aws")
            >>> Beacon.unregister("api_key", namespace="aws")
            True
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

        Examples:
            >>> Beacon.clear()
        """
        with Beacon._lock:
            Beacon._storage.clear()

    @staticmethod
    def clear_expired() -> int:
        """Remove all expired entries, returning count removed.

        Examples:
            >>> Beacon.register("key", "value", ttl=1)
            >>> import time; time.sleep(1.1)
            >>> Beacon.clear_expired()
            1
        """
        count = 0
        current_time = time.time()

        with Beacon._lock:
            keys_to_delete = []
            for key, (_, expiry) in Beacon._storage.items():
                if expiry is not None and current_time > expiry:
                    keys_to_delete.append(key)

            for key in keys_to_delete:
                del Beacon._storage[key]
                count += 1

        return count

    @staticmethod
    def list_keys(*, namespace: str | None = None) -> list[str]:
        """List all registered keys (non-expired), optionally filtered by namespace.

        Examples:
            >>> Beacon.list_keys(namespace="aws")
        """
        current_time = time.time()

        with Beacon._lock:
            keys = []
            for key, (_, expiry) in Beacon._storage.items():
                # Skip expired entries
                if expiry is not None and current_time > expiry:
                    continue

                if namespace is None:
                    keys.append(key)
                else:
                    prefix = f"{namespace}:"
                    if key.startswith(prefix):
                        keys.append(key)

            return keys

    @staticmethod
    def get_namespace(namespace: str) -> dict[str, Any]:
        """Get all non-expired values in a namespace.

        Examples:
            >>> Beacon.get_namespace("aws")
        """
        prefix = f"{namespace}:"
        current_time = time.time()

        with Beacon._lock:
            return {
                key[len(prefix) :]: value
                for key, (value, expiry) in Beacon._storage.items()
                if key.startswith(prefix) and (expiry is None or current_time <= expiry)
            }

    @staticmethod
    def clear_namespace(namespace: str) -> int:
        """Clear all keys in a namespace.

        Examples:
            >>> Beacon.clear_namespace("aws")
        """
        prefix = f"{namespace}:"

        with Beacon._lock:
            keys_to_delete = [key for key in Beacon._storage.keys() if key.startswith(prefix)]
            for key in keys_to_delete:
                del Beacon._storage[key]
            return len(keys_to_delete)

    @staticmethod
    def stats() -> dict[str, int]:
        """Get beacon statistics (hits, misses, size).

        Examples:
            >>> Beacon.clear()
            >>> Beacon.register("key", "value")
            >>> Beacon.get("key")
            'value'
            >>> Beacon.get("missing")
            >>> stats = Beacon.stats()
            >>> stats["hits"]
            1
            >>> stats["misses"]
            1
        """
        with Beacon._lock:
            return {
                "hits": Beacon._stats["hits"],
                "misses": Beacon._stats["misses"],
                "size": len(Beacon._storage),
            }

    @staticmethod
    def reset_stats() -> None:
        """Reset beacon statistics.

        Examples:
            >>> Beacon.reset_stats()
            >>> stats = Beacon.stats()
            >>> stats["hits"]
            0
        """
        with Beacon._lock:
            Beacon._stats["hits"] = 0
            Beacon._stats["misses"] = 0
