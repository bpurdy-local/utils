import time
from typing import Protocol

import requests


class CacheStrategy(Protocol):
    def get(self, key: str) -> requests.Response | None: ...

    def set(self, key: str, response: requests.Response, *, ttl: int) -> None: ...

    def clear(self) -> None: ...


class MemoryCache:
    def __init__(self, *, ttl: int = 3600):
        self.ttl = ttl
        self._cache: dict[str, tuple[requests.Response, float]] = {}

    def get(self, key: str) -> requests.Response | None:
        if key not in self._cache:
            return None

        response, expiry_time = self._cache[key]

        if time.time() > expiry_time:
            del self._cache[key]
            return None

        return response

    def set(self, key: str, response: requests.Response, *, ttl: int | None = None) -> None:
        time_to_live = ttl if ttl is not None else self.ttl
        expiry_time = time.time() + time_to_live
        self._cache[key] = (response, expiry_time)

    def clear(self) -> None:
        self._cache.clear()

    def cleanup_expired(self) -> None:
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry_time) in self._cache.items() if current_time > expiry_time
        ]

        for key in expired_keys:
            del self._cache[key]


class NoCache:
    def get(self, key: str) -> requests.Response | None:
        return None

    def set(self, key: str, response: requests.Response, *, ttl: int) -> None:
        pass

    def clear(self) -> None:
        pass
