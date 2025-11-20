"""Tests for session retry strategies."""

import time

import pytest

from utils.session import (
    CappedRetry,
    ConstantRetry,
    DurationRetry,
    ExponentialRetry,
    FibonacciRetry,
    JitterRetry,
    LinearRetry,
)


class TestExponentialRetry:
    """Test ExponentialRetry strategy."""

    def test_default_params(self):
        """Test with default parameters."""
        retry = ExponentialRetry()
        assert retry.attempts == 3
        assert retry.delay == 1.0
        assert retry.backoff == 2.0

    def test_custom_params(self):
        """Test with custom parameters."""
        retry = ExponentialRetry(attempts=5, delay=0.5, backoff=3.0)
        assert retry.attempts == 5
        assert retry.delay == 0.5
        assert retry.backoff == 3.0

    def test_delay_calculation(self):
        """Test exponential delay calculation."""
        retry = ExponentialRetry(attempts=4, delay=1.0, backoff=2.0)
        assert retry.get_delay(0) == 1.0  # 1.0 * 2^0
        assert retry.get_delay(1) == 2.0  # 1.0 * 2^1
        assert retry.get_delay(2) == 4.0  # 1.0 * 2^2
        assert retry.get_delay(3) == 8.0  # 1.0 * 2^3

    def test_custom_backoff(self):
        """Test with custom backoff factor."""
        retry = ExponentialRetry(attempts=3, delay=2.0, backoff=1.5)
        assert retry.get_delay(0) == 2.0  # 2.0 * 1.5^0
        assert retry.get_delay(1) == 3.0  # 2.0 * 1.5^1
        assert retry.get_delay(2) == 4.5  # 2.0 * 1.5^2


class TestLinearRetry:
    """Test LinearRetry strategy."""

    def test_default_params(self):
        """Test with default parameters."""
        retry = LinearRetry()
        assert retry.attempts == 3
        assert retry.delay == 1.0
        assert retry.backoff == 1.0

    def test_custom_params(self):
        """Test with custom parameters."""
        retry = LinearRetry(attempts=5, delay=2.0, backoff=0.5)
        assert retry.attempts == 5
        assert retry.delay == 2.0
        assert retry.backoff == 0.5

    def test_delay_calculation(self):
        """Test linear delay calculation."""
        retry = LinearRetry(attempts=4, delay=1.0, backoff=1.0)
        assert retry.get_delay(0) == 1.0  # 1.0 * (1 + 1.0 * 0)
        assert retry.get_delay(1) == 2.0  # 1.0 * (1 + 1.0 * 1)
        assert retry.get_delay(2) == 3.0  # 1.0 * (1 + 1.0 * 2)
        assert retry.get_delay(3) == 4.0  # 1.0 * (1 + 1.0 * 3)

    def test_custom_backoff(self):
        """Test with custom backoff factor."""
        retry = LinearRetry(attempts=3, delay=2.0, backoff=0.5)
        assert retry.get_delay(0) == 2.0  # 2.0 * (1 + 0.5 * 0)
        assert retry.get_delay(1) == 3.0  # 2.0 * (1 + 0.5 * 1)
        assert retry.get_delay(2) == 4.0  # 2.0 * (1 + 0.5 * 2)


class TestConstantRetry:
    """Test ConstantRetry strategy."""

    def test_default_params(self):
        """Test with default parameters."""
        retry = ConstantRetry()
        assert retry.attempts == 3
        assert retry.delay == 1.0

    def test_custom_params(self):
        """Test with custom parameters."""
        retry = ConstantRetry(attempts=5, delay=2.5)
        assert retry.attempts == 5
        assert retry.delay == 2.5

    def test_delay_calculation(self):
        """Test constant delay calculation."""
        retry = ConstantRetry(attempts=4, delay=2.0)
        assert retry.get_delay(0) == 2.0
        assert retry.get_delay(1) == 2.0
        assert retry.get_delay(2) == 2.0
        assert retry.get_delay(3) == 2.0


class TestJitterRetry:
    """Test JitterRetry strategy."""

    def test_default_params(self):
        """Test with default parameters."""
        retry = JitterRetry()
        assert retry.attempts == 3
        assert retry.delay == 1.0
        assert retry.backoff == 2.0
        assert retry.jitter_min == 0.5
        assert retry.jitter_max == 1.5

    def test_custom_params(self):
        """Test with custom parameters."""
        retry = JitterRetry(attempts=5, delay=2.0, backoff=3.0, jitter_min=0.8, jitter_max=1.2)
        assert retry.attempts == 5
        assert retry.delay == 2.0
        assert retry.backoff == 3.0
        assert retry.jitter_min == 0.8
        assert retry.jitter_max == 1.2

    def test_delay_range(self):
        """Test that delay falls within jitter range."""
        retry = JitterRetry(attempts=3, delay=1.0, backoff=2.0)
        # For attempt 0: base = 1.0, range = 0.5 to 1.5
        for _ in range(10):
            delay = retry.get_delay(0)
            assert 0.5 <= delay <= 1.5

        # For attempt 1: base = 2.0, range = 1.0 to 3.0
        for _ in range(10):
            delay = retry.get_delay(1)
            assert 1.0 <= delay <= 3.0

    def test_jitter_randomness(self):
        """Test that jitter produces different values."""
        retry = JitterRetry(attempts=3, delay=1.0, backoff=2.0)
        delays = [retry.get_delay(0) for _ in range(20)]
        # Should have some variation (not all identical)
        assert len(set(delays)) > 1


class TestFibonacciRetry:
    """Test FibonacciRetry strategy."""

    def test_default_params(self):
        """Test with default parameters."""
        retry = FibonacciRetry()
        assert retry.attempts == 3
        assert retry.delay == 1.0

    def test_custom_params(self):
        """Test with custom parameters."""
        retry = FibonacciRetry(attempts=6, delay=2.0)
        assert retry.attempts == 6
        assert retry.delay == 2.0

    def test_fibonacci_sequence(self):
        """Test Fibonacci number calculation."""
        retry = FibonacciRetry(attempts=7, delay=1.0)
        assert retry._fibonacci(0) == 1
        assert retry._fibonacci(1) == 1
        assert retry._fibonacci(2) == 2
        assert retry._fibonacci(3) == 3
        assert retry._fibonacci(4) == 5
        assert retry._fibonacci(5) == 8
        assert retry._fibonacci(6) == 13

    def test_delay_calculation(self):
        """Test Fibonacci delay calculation."""
        retry = FibonacciRetry(attempts=6, delay=1.0)
        assert retry.get_delay(0) == 1.0
        assert retry.get_delay(1) == 1.0
        assert retry.get_delay(2) == 2.0
        assert retry.get_delay(3) == 3.0
        assert retry.get_delay(4) == 5.0
        assert retry.get_delay(5) == 8.0

    def test_custom_delay_multiplier(self):
        """Test with custom delay multiplier."""
        retry = FibonacciRetry(attempts=4, delay=2.0)
        assert retry.get_delay(0) == 2.0  # 1 * 2.0
        assert retry.get_delay(1) == 2.0  # 1 * 2.0
        assert retry.get_delay(2) == 4.0  # 2 * 2.0
        assert retry.get_delay(3) == 6.0  # 3 * 2.0


class TestCappedRetry:
    """Test CappedRetry wrapper strategy."""

    def test_caps_exponential_delay(self):
        """Test capping exponential backoff."""
        base = ExponentialRetry(attempts=10, delay=1.0, backoff=2.0)
        retry = CappedRetry(base, max_delay=10.0)

        assert retry.attempts == 10
        assert retry.get_delay(0) == 1.0  # Not capped
        assert retry.get_delay(1) == 2.0  # Not capped
        assert retry.get_delay(2) == 4.0  # Not capped
        assert retry.get_delay(3) == 8.0  # Not capped
        assert retry.get_delay(4) == 10.0  # Capped (would be 16.0)
        assert retry.get_delay(5) == 10.0  # Capped (would be 32.0)

    def test_caps_fibonacci_delay(self):
        """Test capping Fibonacci delays."""
        base = FibonacciRetry(attempts=8, delay=1.0)
        retry = CappedRetry(base, max_delay=5.0)

        assert retry.get_delay(0) == 1.0  # Not capped
        assert retry.get_delay(1) == 1.0  # Not capped
        assert retry.get_delay(2) == 2.0  # Not capped
        assert retry.get_delay(3) == 3.0  # Not capped
        assert retry.get_delay(4) == 5.0  # At cap
        assert retry.get_delay(5) == 5.0  # Capped (would be 8.0)
        assert retry.get_delay(6) == 5.0  # Capped (would be 13.0)

    def test_inherits_attempts(self):
        """Test that attempts are inherited from base strategy."""
        base = LinearRetry(attempts=7, delay=1.0)
        retry = CappedRetry(base, max_delay=10.0)
        assert retry.attempts == 7


class TestDurationRetry:
    """Test DurationRetry strategy."""

    def test_default_params(self):
        """Test with default parameters."""
        retry = DurationRetry(duration=30.0)
        assert retry.duration == 30.0
        assert retry.initial_delay == 0.1
        assert retry.backoff == 1.5
        assert retry.max_delay == 5.0
        assert retry.attempts == 999999  # Very high for duration-based

    def test_custom_params(self):
        """Test with custom parameters."""
        retry = DurationRetry(duration=60.0, initial_delay=0.5, backoff=2.0, max_delay=10.0)
        assert retry.duration == 60.0
        assert retry.initial_delay == 0.5
        assert retry.backoff == 2.0
        assert retry.max_delay == 10.0

    def test_delay_calculation(self):
        """Test exponential delay calculation with cap."""
        retry = DurationRetry(duration=60.0, initial_delay=1.0, backoff=2.0, max_delay=10.0)
        assert retry.get_delay(0) == 1.0  # 1.0 * 2^0
        assert retry.get_delay(1) == 2.0  # 1.0 * 2^1
        assert retry.get_delay(2) == 4.0  # 1.0 * 2^2
        assert retry.get_delay(3) == 8.0  # 1.0 * 2^3
        assert retry.get_delay(4) == 10.0  # Capped (would be 16.0)
        assert retry.get_delay(5) == 10.0  # Capped (would be 32.0)

    def test_reset_timer(self):
        """Test resetting the timer."""
        retry = DurationRetry(duration=1.0)
        assert retry._start_time is None

        retry.reset()
        assert retry._start_time is not None
        assert retry._elapsed_time == 0.0

    def test_should_retry_initially(self):
        """Test should_retry returns True initially."""
        retry = DurationRetry(duration=1.0)
        assert retry.should_retry() is True
        assert retry._start_time is not None  # Auto-initialized

    def test_should_retry_within_duration(self):
        """Test should_retry returns True within duration."""
        retry = DurationRetry(duration=2.0)
        retry.reset()
        time.sleep(0.1)
        assert retry.should_retry() is True

    @pytest.mark.slow
    def test_should_retry_after_duration(self):
        """Test should_retry returns False after duration."""
        retry = DurationRetry(duration=0.2)
        retry.reset()
        time.sleep(0.3)
        assert retry.should_retry() is False

    def test_elapsed_time_tracking(self):
        """Test elapsed time is tracked."""
        retry = DurationRetry(duration=10.0)
        retry.reset()
        time.sleep(0.1)
        retry.should_retry()
        assert retry._elapsed_time >= 0.1
