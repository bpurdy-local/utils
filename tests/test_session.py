"""Tests for Session class."""

import re
from unittest.mock import Mock, patch

import pytest
import requests

from utils.session import (
    BearerAuth,
    ConstantRetry,
    ExponentialRetry,
    Session,
)


class TestSessionInitialization:
    """Test Session initialization."""

    def test_default_initialization(self):
        """Test Session with default parameters."""
        session = Session()
        assert session.timeout == 30
        assert isinstance(session.metrics, dict)
        assert len(session.metrics) == 0
        assert session.handle_rate_limit is True
        assert session.rate_limit_max_wait == 60.0

    def test_custom_timeout(self):
        """Test Session with custom timeout."""
        session = Session(timeout=60)
        assert session.timeout == 60

    def test_custom_headers(self):
        """Test Session with custom headers."""
        headers = {"User-Agent": "TestAgent/1.0", "Accept": "application/json"}
        session = Session(headers=headers)
        assert session.headers["User-Agent"] == "TestAgent/1.0"
        assert session.headers["Accept"] == "application/json"

    def test_with_auth(self):
        """Test Session with auth parameter."""
        auth = BearerAuth("test-token")
        session = Session(auth=auth)
        assert session.headers["Authorization"] == "Bearer test-token"

    def test_rate_limit_config(self):
        """Test Session with custom rate limit config."""
        session = Session(handle_rate_limit=False, rate_limit_max_wait=30.0)
        assert session.handle_rate_limit is False
        assert session.rate_limit_max_wait == 30.0

    def test_inherits_from_requests_session(self):
        """Test that Session inherits from requests.Session."""
        session = Session()
        assert isinstance(session, requests.Session)


class TestSessionHeaders:
    """Test Session header management."""

    def test_set_default_header(self):
        """Test setting a default header."""
        session = Session()
        session.set_default_header("X-Custom-Header", "custom-value")
        assert session.headers["X-Custom-Header"] == "custom-value"

    def test_update_existing_header(self):
        """Test updating an existing header."""
        session = Session(headers={"User-Agent": "Agent1"})
        session.set_default_header("User-Agent", "Agent2")
        assert session.headers["User-Agent"] == "Agent2"

    def test_multiple_headers(self):
        """Test setting multiple headers."""
        session = Session()
        session.set_default_header("X-Header-1", "value1")
        session.set_default_header("X-Header-2", "value2")
        session.set_default_header("X-Header-3", "value3")

        assert session.headers["X-Header-1"] == "value1"
        assert session.headers["X-Header-2"] == "value2"
        assert session.headers["X-Header-3"] == "value3"


class TestSessionMetrics:
    """Test Session metrics tracking."""

    def test_add_url_pattern(self):
        """Test adding URL patterns."""
        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")

        assert "users" in session.metrics
        assert session.metrics["users"]["count"] == 0

    def test_add_multiple_patterns(self):
        """Test adding multiple URL patterns."""
        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")
        session.add_url_pattern(r"/api/orders", tag="orders")
        session.add_url_pattern(r"/api/products", tag="products")

        assert len(session.metrics) == 3
        assert "users" in session.metrics
        assert "orders" in session.metrics
        assert "products" in session.metrics

    def test_pattern_compilation(self):
        """Test that patterns are compiled correctly."""
        session = Session()
        session.add_url_pattern(r"/api/users/\d+", tag="user_detail")

        # Check pattern was added
        assert len(session._url_patterns) == 1
        pattern_config = session._url_patterns[0]
        assert pattern_config["tag"] == "user_detail"
        assert isinstance(pattern_config["pattern"], re.Pattern)

    def test_match_url_pattern(self):
        """Test URL pattern matching."""
        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")
        session.add_url_pattern(r"/api/orders/\d+", tag="order_detail")

        # Test matches
        match1 = session._match_url_pattern("https://api.example.com/api/users")
        assert match1 is not None
        assert match1["tag"] == "users"

        match2 = session._match_url_pattern("https://api.example.com/api/orders/123")
        assert match2 is not None
        assert match2["tag"] == "order_detail"

        # Test non-match
        match3 = session._match_url_pattern("https://api.example.com/api/products")
        assert match3 is None

    def test_increment_metric(self):
        """Test incrementing metrics."""
        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")

        session._increment_metric("users")
        assert session.metrics["users"]["count"] == 1

        session._increment_metric("users")
        assert session.metrics["users"]["count"] == 2

    def test_reset_metrics(self):
        """Test resetting metrics."""
        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")
        session._increment_metric("users")
        session._increment_metric("users")

        assert session.metrics["users"]["count"] == 2
        session.reset_metrics()
        assert session.metrics["users"]["count"] == 0

    def test_get_metrics(self):
        """Test getting metrics copy."""
        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")
        session._increment_metric("users")

        metrics = session.get_metrics()
        assert metrics["users"]["count"] == 1
        assert metrics is not session.metrics

    def test_compare_metrics(self):
        """Test comparing metrics snapshots."""
        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")
        session.add_url_pattern(r"/api/orders", tag="orders")

        snapshot = session.get_metrics()

        session._increment_metric("users")
        session._increment_metric("users")
        session._increment_metric("orders")

        diff = session.compare_metrics(snapshot)
        assert diff["users"]["count"] == 2
        assert diff["orders"]["count"] == 1

    def test_compare_metrics_no_changes(self):
        """Test comparing metrics with no changes."""
        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")

        snapshot = session.get_metrics()
        diff = session.compare_metrics(snapshot)
        assert diff == {}

    def test_compare_metrics_new_tags(self):
        """Test comparing metrics with new tags."""
        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")

        snapshot = session.get_metrics()

        session.add_url_pattern(r"/api/orders", tag="orders")
        session._increment_metric("orders")

        diff = session.compare_metrics(snapshot)
        assert diff["orders"]["count"] == 1

    @patch("requests.Session.request")
    def test_unmatched_url_tracking(self, mock_request):
        """Test that unmatched URLs are tracked under Unknown tag."""
        mock_request.return_value = Mock(status_code=200)

        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")

        session.request("GET", "https://api.example.com/api/users")
        assert session.metrics["users"]["count"] == 1
        assert "Unknown" not in session.metrics

        session.request("GET", "https://api.example.com/other/endpoint")
        assert session.metrics["Unknown"]["count"] == 1

        session.request("GET", "https://api.example.com/another/path")
        assert session.metrics["Unknown"]["count"] == 2


class TestSessionRequest:
    """Test Session request method."""

    @patch("requests.Session.request")
    def test_default_timeout_injection(self, mock_request):
        """Test that default timeout is injected."""
        mock_request.return_value = Mock(status_code=200)

        session = Session(timeout=45)
        session.request("GET", "https://api.example.com/test")

        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["timeout"] == 45

    @patch("requests.Session.request")
    def test_explicit_timeout_not_overridden(self, mock_request):
        """Test that explicit timeout is not overridden."""
        mock_request.return_value = Mock(status_code=200)

        session = Session(timeout=30)
        session.request("GET", "https://api.example.com/test", timeout=60)

        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["timeout"] == 60

    @patch("requests.Session.request")
    def test_metrics_tracking_on_request(self, mock_request):
        """Test that metrics are tracked on requests."""
        mock_request.return_value = Mock(status_code=200)

        session = Session()
        session.add_url_pattern(r"/api/users", tag="users")

        session.request("GET", "https://api.example.com/api/users")
        assert session.metrics["users"]["count"] == 1

        session.request("GET", "https://api.example.com/api/users/123")
        assert session.metrics["users"]["count"] == 2


class TestSessionRetry:
    """Test Session retry functionality."""

    @patch("requests.Session.request")
    def test_retry_on_failure(self, mock_request):
        """Test retry on request failure."""
        # Fail twice, then succeed
        mock_request.side_effect = [
            requests.RequestException("Error 1"),
            requests.RequestException("Error 2"),
            Mock(status_code=200),
        ]

        session = Session()
        retry = ExponentialRetry(attempts=3, delay=0.01, backoff=1.0)
        session.add_url_pattern(r"/api/test", tag="test", retry=retry)

        response = session.request("GET", "https://api.example.com/api/test")
        assert response.status_code == 200
        assert mock_request.call_count == 3

    @patch("requests.Session.request")
    @patch("time.sleep")
    def test_retry_with_delays(self, mock_sleep, mock_request):
        """Test that retry delays are applied."""
        mock_request.side_effect = [
            requests.RequestException("Error 1"),
            requests.RequestException("Error 2"),
            Mock(status_code=200),
        ]

        session = Session()
        retry = ConstantRetry(attempts=3, delay=1.0)
        session.add_url_pattern(r"/api/test", tag="test", retry=retry)

        session.request("GET", "https://api.example.com/api/test")

        # Should have slept twice (after first and second failures)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1.0)

    @patch("requests.Session.request")
    def test_retry_exhaustion(self, mock_request):
        """Test that retry attempts are exhausted."""
        mock_request.side_effect = requests.RequestException("Always fails")

        session = Session()
        retry = ExponentialRetry(attempts=2, delay=0.01, backoff=1.0)
        session.add_url_pattern(r"/api/test", tag="test", retry=retry)

        with pytest.raises(requests.RequestException):
            session.request("GET", "https://api.example.com/api/test")

        # Initial attempt + 2 retries = 3 total calls
        assert mock_request.call_count == 3

    @patch("requests.Session.request")
    def test_no_retry_without_pattern(self, mock_request):
        """Test that requests without retry pattern don't retry."""
        mock_request.side_effect = requests.RequestException("Error")

        session = Session()

        with pytest.raises(requests.RequestException):
            session.request("GET", "https://api.example.com/api/test")

        # Only one attempt (no retries)
        assert mock_request.call_count == 1


class TestSessionRateLimiting:
    """Test Session rate limiting functionality."""

    @patch("requests.Session.request")
    @patch("time.sleep")
    def test_rate_limit_with_retry_after_header(self, mock_sleep, mock_request):
        """Test rate limiting with Retry-After header."""
        # First call returns 429, second succeeds
        response_429 = Mock(status_code=429, headers={"Retry-After": "2"})
        response_200 = Mock(status_code=200)
        mock_request.side_effect = [response_429, response_200]

        session = Session(handle_rate_limit=True)
        response = session.request("GET", "https://api.example.com/test")

        assert response.status_code == 200
        mock_sleep.assert_called_once_with(2.0)

    @patch("requests.Session.request")
    @patch("time.sleep")
    def test_rate_limit_max_wait(self, mock_sleep, mock_request):
        """Test rate limit max wait cap."""
        # Retry-After is 120 seconds, but max_wait is 60
        response_429 = Mock(status_code=429, headers={"Retry-After": "120"})
        response_200 = Mock(status_code=200)
        mock_request.side_effect = [response_429, response_200]

        session = Session(handle_rate_limit=True, rate_limit_max_wait=60.0)
        session.request("GET", "https://api.example.com/test")

        # Should sleep for max_wait, not the full 120 seconds
        mock_sleep.assert_called_once_with(60.0)

    @patch("requests.Session.request")
    def test_rate_limit_disabled(self, mock_request):
        """Test that rate limiting can be disabled."""
        response_429 = Mock(status_code=429, headers={"Retry-After": "2"})
        mock_request.return_value = response_429

        session = Session(handle_rate_limit=False)
        response = session.request("GET", "https://api.example.com/test")

        # Should return 429 without retrying
        assert response.status_code == 429


class TestSessionParseRetryAfter:
    """Test Session._parse_retry_after method."""

    def test_parse_numeric_seconds(self):
        """Test parsing numeric Retry-After value."""
        session = Session()
        assert session._parse_retry_after("5") == 5.0
        assert session._parse_retry_after("10") == 10.0
        assert session._parse_retry_after("0.5") == 0.5

    def test_parse_http_date(self):
        """Test parsing HTTP date Retry-After value."""
        from datetime import UTC, datetime, timedelta

        session = Session()

        # Create a date 5 seconds in the future
        future_date = datetime.now(UTC) + timedelta(seconds=5)
        date_str = future_date.strftime("%a, %d %b %Y %H:%M:%S GMT")

        delay = session._parse_retry_after(date_str)
        # Should be approximately 5 seconds (allow wider tolerance for execution time)
        assert 3.0 <= delay <= 6.0

    def test_parse_invalid_value(self):
        """Test parsing invalid Retry-After value."""
        session = Session()
        # Should return default 1.0 on parse error
        assert session._parse_retry_after("invalid") == 1.0

    def test_parse_past_date(self):
        """Test parsing HTTP date in the past."""
        from datetime import UTC, datetime, timedelta

        session = Session()

        # Create a date in the past
        past_date = datetime.now(UTC) - timedelta(seconds=10)
        date_str = past_date.strftime("%a, %d %b %Y %H:%M:%S GMT")

        delay = session._parse_retry_after(date_str)
        # Should return 0 (max with 0)
        assert delay == 0.0


class TestSessionGetJson:
    """Test Session.get_json method."""

    @patch("requests.Session.get")
    def test_get_json_success(self, mock_get):
        """Test successful JSON retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {"key": "value", "number": 42}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        session = Session()
        data = session.get_json("https://api.example.com/data")

        assert data == {"key": "value", "number": 42}
        mock_response.raise_for_status.assert_called_once()

    @patch("requests.Session.get")
    def test_get_json_with_params(self, mock_get):
        """Test get_json with query parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        session = Session()
        params = {"page": 1, "limit": 10}
        session.get_json("https://api.example.com/data", params=params)

        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["params"] == params

    @patch("requests.Session.get")
    def test_get_json_http_error(self, mock_get):
        """Test get_json with HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        session = Session()

        with pytest.raises(requests.HTTPError):
            session.get_json("https://api.example.com/data")


class TestSessionIntegration:
    """Integration tests for Session class."""

    def test_session_with_all_features(self):
        """Test Session with multiple features enabled."""
        session = Session(
            timeout=60,
            headers={"User-Agent": "TestAgent/1.0"},
            auth=BearerAuth("test-token"),
            handle_rate_limit=True,
        )

        # Verify all features are configured
        assert session.timeout == 60
        assert session.headers["User-Agent"] == "TestAgent/1.0"
        assert session.headers["Authorization"] == "Bearer test-token"
        assert session.handle_rate_limit is True

    def test_context_manager_support(self):
        """Test Session as context manager."""
        with Session(timeout=30) as session:
            assert isinstance(session, Session)
            assert session.timeout == 30

        # Session should be closed after context
        # (Note: requests.Session.close() is called automatically)

    @patch("requests.Session.request")
    def test_metrics_and_retry_integration(self, mock_request):
        """Test metrics tracking with retry logic."""
        # Fail once, then succeed
        mock_request.side_effect = [
            requests.RequestException("Error"),
            Mock(status_code=200),
        ]

        session = Session()
        retry = ExponentialRetry(attempts=2, delay=0.01, backoff=1.0)
        session.add_url_pattern(r"/api/users", tag="users", retry=retry)

        session.request("GET", "https://api.example.com/api/users")

        assert session.metrics["users"]["count"] == 1
