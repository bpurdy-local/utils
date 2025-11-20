"""Enhanced HTTP session with retry, rate limiting, and metrics tracking."""

import hashlib
import time
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

import requests

from utils.logger import Logger

if TYPE_CHECKING:
    from utils.session.auth import Auth
    from utils.session.batch import BatchRequest
    from utils.session.cache import CacheStrategy
    from utils.session.retry import Retry


class Session(requests.Session):
    """Enhanced requests.Session with default timeout and convenient auth helpers.

    Inherits all methods from requests.Session (get, post, put, delete, etc.)
    and adds utilities for common patterns.

    Example:
        from utils import Session
        from utils.session import BearerAuth

        # Using auth classes (recommended)
        session = Session(timeout=30, auth=BearerAuth("your-token"))

        # Or using dict-based config (backward compatible)
        session = Session(timeout=30, auth={"type": "bearer", "token": "your-token"})

        # Configure URL patterns with tags and retry logic
        from utils.session import Retry
        session.add_url_pattern(r"/api/users", tag="users_api", retry=Retry(attempts=3))
        session.add_url_pattern(
            r"/api/orders", tag="orders_api", retry=Retry(attempts=5, delay=2.0)
        )

        data = session.get_json("https://api.example.com/users")
        print(session.metrics)  # {"users_api": 1}
    """

    def __init__(
        self,
        *,
        timeout: int = 30,
        headers: dict[str, str] | None = None,
        auth: "Auth | dict[str, Any] | None" = None,
        handle_rate_limit: bool = True,
        rate_limit_max_wait: float = 60.0,
        cache: "CacheStrategy | None" = None,
    ):
        """Initialize session with default timeout and optional headers/auth.

        Args:
            timeout: Default timeout in seconds for all requests (default: 30)
            headers: Optional dict of default headers to set
            auth: Optional auth - can be an Auth object (BearerAuth, BasicAuth, etc.)
                  or a dict with 'type' key for backward compatibility
            handle_rate_limit: Automatically handle 429 responses (default: True)
            rate_limit_max_wait: Maximum seconds to wait for rate limit (default: 60.0)
            cache: Optional cache strategy for GET requests (default: None)
        """
        super().__init__()
        self.timeout = timeout
        self.metrics: dict[str, dict[str, Any]] = {}
        self._url_patterns: list[dict[str, Any]] = []
        self.handle_rate_limit = handle_rate_limit
        self.rate_limit_max_wait = rate_limit_max_wait
        self._cache = cache
        self._request_hooks: list[Callable[[requests.PreparedRequest], None]] = []
        self._response_hooks: list[Callable[[requests.Response], None]] = []

        if headers:
            self.headers.update(headers)
        if auth:
            self.set_auth(auth)

    def add_url_pattern(self, pattern: str, *, tag: str, retry: "Retry | None" = None) -> None:
        """Add a URL pattern with associated tag and retry configuration.

        Args:
            pattern: Regex pattern to match against URLs
            tag: Tag name for metrics tracking
            retry: Optional Retry object for retry configuration

        Example:
            from utils.session import Retry

            session.add_url_pattern(r"/api/users", tag="users_api", retry=Retry(attempts=3))
            session.add_url_pattern(
                r"/api/orders/\\d+",
                tag="orders_api",
                retry=Retry(attempts=5, delay=2.0, backoff=2.0)
            )
        """
        import re

        compiled_pattern = re.compile(pattern)
        self._url_patterns.append({"pattern": compiled_pattern, "tag": tag, "retry": retry})
        self.metrics.setdefault(
            tag,
            {
                "count": 0,
                "latencies": [],
                "errors": 0,
                "status_codes": {},
            },
        )

    def _match_url_pattern(self, url: str) -> dict[str, Any] | None:
        """Find the first matching pattern for a URL.

        Args:
            url: URL to match against patterns

        Returns:
            Pattern config dict if match found, None otherwise
        """
        for pattern_config in self._url_patterns:
            if pattern_config["pattern"].search(url):
                return pattern_config
        return None

    def _increment_metric(self, tag: str) -> None:
        """Increment metric counter for a tag.

        Args:
            tag: Metric tag to increment
        """
        if tag not in self.metrics:
            self.metrics[tag] = {
                "count": 0,
                "latencies": [],
                "errors": 0,
                "status_codes": {},
            }
        self.metrics[tag]["count"] += 1

    def _record_latency(self, tag: str, latency: float) -> None:
        """Record request latency for a tag."""
        if tag in self.metrics:
            self.metrics[tag]["latencies"].append(latency)

    def _record_error(self, tag: str) -> None:
        """Record an error for a tag."""
        if tag in self.metrics:
            self.metrics[tag]["errors"] += 1

    def _record_status_code(self, tag: str, status_code: int) -> None:
        """Record a status code for a tag."""
        if tag in self.metrics:
            status_codes = self.metrics[tag]["status_codes"]
            status_codes[status_code] = status_codes.get(status_code, 0) + 1

    def _parse_retry_after(self, retry_after: str) -> float:
        """Parse Retry-After header value (seconds or HTTP date).

        Args:
            retry_after: Value from Retry-After header

        Returns:
            Delay in seconds (minimum 0, default 1.0 on parse error)
        """
        # Try parsing as numeric seconds
        try:
            return float(retry_after)
        except ValueError:
            pass

        # Try parsing as HTTP date
        try:
            from datetime import UTC, datetime
            from email.utils import parsedate_to_datetime

            retry_date = parsedate_to_datetime(retry_after)
            now = datetime.now(UTC)
            delta = (retry_date - now).total_seconds()
            return max(0, delta)
        except (ValueError, TypeError):
            Logger.warning(
                {"message": "Failed to parse Retry-After header", "retry_after": retry_after}
            )
            return 1.0

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        cache_key = self._generate_cache_key(method, url, kwargs)

        if method.upper() == "GET" and self._cache:
            cached_response = self._cache.get(cache_key)
            if cached_response:
                return cached_response

        self._ensure_timeout(kwargs)
        pattern_config = self._track_request_metrics(url)
        retry_config = self._get_retry_config(pattern_config)

        tag = pattern_config["tag"] if pattern_config else "Unknown"
        start_time = time.time()

        try:
            if retry_config:
                response = self._request_with_retry(method, url, retry_config, kwargs)
            else:
                response = self._request_with_rate_limit_handling(method, url, kwargs)

            latency = time.time() - start_time
            self._record_latency(tag, latency)
            self._record_status_code(tag, response.status_code)

            if method.upper() == "GET" and self._cache and response.status_code == 200:
                self._cache.set(cache_key, response, ttl=3600)

            return response

        except Exception:
            self._record_error(tag)
            raise

    def _generate_cache_key(self, method: str, url: str, kwargs: dict[str, Any]) -> str:
        params = kwargs.get("params", {})
        key_parts = [method, url, str(sorted(params.items()) if params else "")]
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _ensure_timeout(self, kwargs: dict[str, Any]) -> None:
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout

    def _track_request_metrics(self, url: str) -> dict[str, Any] | None:
        """Track metrics for the request URL and return pattern config if matched."""
        pattern_config = self._match_url_pattern(url)

        if pattern_config:
            self._increment_metric(pattern_config["tag"])
        else:
            self._increment_metric("Unknown")

        return pattern_config

    def _get_retry_config(self, pattern_config: dict[str, Any] | None) -> "Retry | None":
        """Extract retry configuration from pattern config."""
        if pattern_config is None:
            return None
        return pattern_config.get("retry")

    def _request_with_retry(
        self,
        method: str,
        url: str,
        retry_config: "Retry",
        kwargs: dict[str, Any],
    ) -> requests.Response:
        """Execute request with retry logic."""
        self._prepare_retry_config(retry_config)
        max_attempts = retry_config.attempts + 1
        attempt = 0

        while attempt < max_attempts:
            if self._should_stop_retrying(retry_config):
                break

            try:
                response = super().request(method, url, **kwargs)

                if self._should_handle_rate_limit(response) and self._handle_rate_limit_in_retry(
                    response, retry_config, attempt, max_attempts
                ):
                    attempt += 1
                    continue

                response.raise_for_status()
                return response

            except (requests.RequestException, requests.HTTPError) as error:
                if self._should_reraise_immediately(error):
                    raise

                if self._is_last_attempt(attempt, max_attempts):
                    raise

                self._wait_before_retry(retry_config, attempt)
                attempt += 1

        return super().request(method, url, **kwargs)

    def _prepare_retry_config(self, retry_config: "Retry") -> None:
        """Prepare retry configuration (e.g., reset timers for duration-based retries)."""
        if hasattr(retry_config, "reset"):
            retry_config.reset()

    def _should_stop_retrying(self, retry_config: "Retry") -> bool:
        """Check if we should stop retrying (for duration-based retries)."""
        if hasattr(retry_config, "should_retry"):
            return not retry_config.should_retry()
        return False

    def _should_handle_rate_limit(self, response: requests.Response) -> bool:
        """Check if response is a rate limit error that we should handle."""
        return response.status_code == 429 and self.handle_rate_limit

    def _handle_rate_limit_in_retry(
        self,
        response: requests.Response,
        retry_config: "Retry",
        attempt: int,
        max_attempts: int,
    ) -> bool:
        """Handle rate limit during retry. Returns True if we should continue retry loop."""
        wait_time = self._calculate_rate_limit_wait_time(response, retry_config, attempt)

        if not self._is_last_attempt(attempt, max_attempts):
            time.sleep(wait_time)
            return True

        return False

    def _calculate_rate_limit_wait_time(
        self,
        response: requests.Response,
        retry_config: "Retry",
        attempt: int,
    ) -> float:
        """Calculate how long to wait for rate limit."""
        retry_after = response.headers.get("Retry-After")

        if retry_after:
            wait_time = self._parse_retry_after(retry_after)
        else:
            wait_time = retry_config.get_delay(attempt)

        return min(wait_time, self.rate_limit_max_wait)

    def _should_reraise_immediately(self, error: Exception) -> bool:
        """Check if error should be re-raised immediately without retry."""
        if isinstance(error, requests.HTTPError):
            return error.response.status_code == 429
        return False

    def _is_last_attempt(self, attempt: int, max_attempts: int) -> bool:
        """Check if this is the last retry attempt."""
        return attempt >= max_attempts - 1

    def _wait_before_retry(self, retry_config: "Retry", attempt: int) -> None:
        """Wait before the next retry attempt."""
        delay = retry_config.get_delay(attempt)
        time.sleep(delay)

    def _request_with_rate_limit_handling(
        self,
        method: str,
        url: str,
        kwargs: dict[str, Any],
    ) -> requests.Response:
        """Execute request with rate limit handling but no retry logic."""
        response = super().request(method, url, **kwargs)

        if self._should_handle_rate_limit(response):
            wait_time = self._get_simple_rate_limit_wait_time(response)
            time.sleep(wait_time)
            response = super().request(method, url, **kwargs)

        return response

    def _get_simple_rate_limit_wait_time(self, response: requests.Response) -> float:
        """Get wait time for rate limit without retry config."""
        retry_after = response.headers.get("Retry-After")

        if retry_after:
            wait_time = self._parse_retry_after(retry_after)
            return min(wait_time, self.rate_limit_max_wait)

        return 1.0

    def reset_metrics(self) -> None:
        for tag in self.metrics:
            self.metrics[tag] = {
                "count": 0,
                "latencies": [],
                "errors": 0,
                "status_codes": {},
            }

    def get_metrics(self) -> dict[str, dict[str, Any]]:
        import copy

        return copy.deepcopy(self.metrics)

    def get_metrics_summary(self) -> dict[str, dict[str, Any]]:
        summary = {}
        for tag, data in self.metrics.items():
            latencies = data["latencies"]
            avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

            summary[tag] = {
                "count": data["count"],
                "errors": data["errors"],
                "avg_latency": avg_latency,
                "status_codes": data["status_codes"].copy(),
            }
        return summary

    def compare_metrics(self, snapshot: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        """Compare current metrics with a previous snapshot.

        Args:
            snapshot: Previous metrics snapshot (from get_metrics())

        Returns:
            Dictionary showing the difference in request counts for each tag

        Example:
            snapshot = session.get_metrics()
            # ... make some requests ...
            diff = session.compare_metrics(snapshot)
            print(diff)  # {"users_api": 5, "orders_api": 2}
        """
        result = {}
        all_tags = set(self.metrics.keys()) | set(snapshot.keys())

        for tag in all_tags:
            current_data = self.metrics.get(tag, {"count": 0, "errors": 0})
            previous_data = snapshot.get(tag, {"count": 0, "errors": 0})

            count_diff = current_data["count"] - previous_data["count"]
            errors_diff = current_data["errors"] - previous_data["errors"]

            if count_diff != 0 or errors_diff != 0:
                result[tag] = {"count": count_diff, "errors": errors_diff}

        return result

    def set_default_header(self, name: str, value: str) -> None:
        """Set a default header for all subsequent requests.

        Args:
            name: Header name
            value: Header value
        """
        self.headers[name] = value

    def set_auth(self, auth: "Auth | dict[str, Any]") -> None:
        """Set authentication using an auth object or dict config.

        Args:
            auth: Auth object (BearerAuth, BasicAuth, etc.) or dict with 'type' key

        Examples:
            from utils.session import BearerAuth, BasicAuth, APIKeyAuth

            # Using auth classes (recommended)
            session.set_auth(BearerAuth("your-token"))
            session.set_auth(BasicAuth("username", "password"))
            session.set_auth(APIKeyAuth("your-key", header_name="X-API-Key"))

            # Using dict config (backward compatible)
            session.set_auth({"type": "bearer", "token": "your-token"})
            session.set_auth({"type": "basic", "username": "user", "password": "pass"})
        """
        if hasattr(auth, "apply"):
            # Auth object with apply() method
            auth.apply(self)
        elif isinstance(auth, dict):
            # Dict-based auth for backward compatibility
            from utils.session.auth import BasicAuth, BearerAuth

            auth_type = auth.get("type", "").lower()
            if auth_type == "bearer":
                token = auth.get("token", "")
                BearerAuth(token).apply(self)
            elif auth_type == "basic":
                username = auth.get("username", "")
                password = auth.get("password", "")
                BasicAuth(username, password).apply(self)
            else:
                # Fall back to requests' native auth
                self.auth = auth
        else:
            # Assume it's a requests-compatible auth object
            self.auth = auth

    def get_json(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        **kwargs,
    ) -> Any:
        response = self.get(url, params=params, **kwargs)
        response.raise_for_status()
        return response.json()

    def add_request_hook(self, hook: Callable[[requests.PreparedRequest], None]) -> None:
        self._request_hooks.append(hook)

    def add_response_hook(self, hook: Callable[[requests.Response], None]) -> None:
        self._response_hooks.append(hook)

    def clear_hooks(self) -> None:
        self._request_hooks.clear()
        self._response_hooks.clear()

    def batch_request(
        self, *request_groups: "BatchRequest | list[BatchRequest]"
    ) -> list[requests.Response]:
        from utils.session.batch import BatchExecutor

        executor = BatchExecutor(self)
        return executor.execute(*request_groups)

    def stream_download(self, url: str, *, output_path: str | Path, chunk_size: int = 8192) -> None:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with self.get(url, stream=True) as response:
            response.raise_for_status()

            with open(output_file, "wb") as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)
