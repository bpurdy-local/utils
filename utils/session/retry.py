"""Retry strategies for HTTP requests."""

import random
from typing import Protocol


class Retry(Protocol):
    """Protocol for retry strategies."""

    attempts: int

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt number.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds for this attempt
        """
        ...


class ExponentialRetry:
    """Exponential backoff retry strategy.

    Delay increases exponentially: delay * (backoff ** attempt)
    Example with delay=1.0, backoff=2.0: 1s, 2s, 4s, 8s, 16s
    """

    def __init__(self, *, attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
        """Initialize exponential retry strategy.

        Args:
            attempts: Number of retry attempts (default: 3)
            delay: Initial delay in seconds (default: 1.0)
            backoff: Backoff multiplier (default: 2.0)

        Example:
            retry = ExponentialRetry(attempts=4, delay=1.0, backoff=2.0)
            # Delays: 1s, 2s, 4s, 8s
        """
        self.attempts = attempts
        self.delay = delay
        self.backoff = backoff

    def get_delay(self, attempt: int) -> float:
        """Calculate exponential delay."""
        return self.delay * (self.backoff**attempt)


class LinearRetry:
    """Linear backoff retry strategy.

    Delay increases linearly: delay * (1 + backoff * attempt)
    Example with delay=1.0, backoff=1.0: 1s, 2s, 3s, 4s, 5s
    """

    def __init__(self, *, attempts: int = 3, delay: float = 1.0, backoff: float = 1.0):
        """Initialize linear retry strategy.

        Args:
            attempts: Number of retry attempts (default: 3)
            delay: Initial delay in seconds (default: 1.0)
            backoff: Linear increment multiplier (default: 1.0)

        Example:
            retry = LinearRetry(attempts=4, delay=1.0, backoff=1.0)
            # Delays: 1s, 2s, 3s, 4s
        """
        self.attempts = attempts
        self.delay = delay
        self.backoff = backoff

    def get_delay(self, attempt: int) -> float:
        """Calculate linear delay."""
        return self.delay * (1 + self.backoff * attempt)


class ConstantRetry:
    """Constant delay retry strategy.

    Same delay for every retry attempt.
    Example with delay=2.0: 2s, 2s, 2s, 2s
    """

    def __init__(self, *, attempts: int = 3, delay: float = 1.0):
        """Initialize constant retry strategy.

        Args:
            attempts: Number of retry attempts (default: 3)
            delay: Delay in seconds for all retries (default: 1.0)

        Example:
            retry = ConstantRetry(attempts=5, delay=2.0)
            # Delays: 2s, 2s, 2s, 2s, 2s
        """
        self.attempts = attempts
        self.delay = delay

    def get_delay(self, attempt: int) -> float:
        """Calculate constant delay."""
        return self.delay


class JitterRetry:
    """Exponential backoff with random jitter.

    Adds randomness to prevent thundering herd problem.
    Delay: (delay * backoff ** attempt) * random(0.5 to 1.5)
    """

    def __init__(
        self,
        *,
        attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        jitter_min: float = 0.5,
        jitter_max: float = 1.5,
    ):
        """Initialize jitter retry strategy.

        Args:
            attempts: Number of retry attempts (default: 3)
            delay: Initial delay in seconds (default: 1.0)
            backoff: Backoff multiplier (default: 2.0)
            jitter_min: Minimum jitter multiplier (default: 0.5)
            jitter_max: Maximum jitter multiplier (default: 1.5)

        Example:
            retry = JitterRetry(attempts=4, delay=1.0, backoff=2.0)
            # Delays: ~1s, ~2s, ~4s, ~8s (with random variation)
        """
        self.attempts = attempts
        self.delay = delay
        self.backoff = backoff
        self.jitter_min = jitter_min
        self.jitter_max = jitter_max

    def get_delay(self, attempt: int) -> float:
        """Calculate delay with jitter."""
        base_delay = self.delay * (self.backoff**attempt)
        jitter_multiplier = random.uniform(self.jitter_min, self.jitter_max)
        return base_delay * jitter_multiplier


class FibonacciRetry:
    """Fibonacci sequence retry strategy.

    Delay follows Fibonacci sequence multiplied by base delay.
    Example with delay=1.0: 1s, 1s, 2s, 3s, 5s, 8s, 13s
    """

    def __init__(self, *, attempts: int = 3, delay: float = 1.0):
        """Initialize Fibonacci retry strategy.

        Args:
            attempts: Number of retry attempts (default: 3)
            delay: Base delay multiplier in seconds (default: 1.0)

        Example:
            retry = FibonacciRetry(attempts=6, delay=1.0)
            # Delays: 1s, 1s, 2s, 3s, 5s, 8s
        """
        self.attempts = attempts
        self.delay = delay

    def _fibonacci(self, n: int) -> int:
        """Calculate nth Fibonacci number."""
        if n <= 1:
            return 1

        previous, current = 1, 1
        for _ in range(n - 1):
            previous, current = current, previous + current
        return current

    def get_delay(self, attempt: int) -> float:
        """Calculate Fibonacci delay."""
        return self.delay * self._fibonacci(attempt)


class CappedRetry:
    """Wrapper that caps maximum delay for any retry strategy.

    Useful for preventing extremely long delays in exponential strategies.
    """

    def __init__(self, strategy: Retry, *, max_delay: float):
        """Initialize capped retry wrapper.

        Args:
            strategy: Underlying retry strategy to wrap
            max_delay: Maximum delay cap in seconds

        Example:
            base = ExponentialRetry(attempts=10, delay=1.0, backoff=2.0)
            retry = CappedRetry(base, max_delay=30.0)
            # Delays capped at 30 seconds max
        """
        self.attempts = strategy.attempts
        self.strategy = strategy
        self.max_delay = max_delay

    def get_delay(self, attempt: int) -> float:
        """Calculate delay with cap applied."""
        uncapped_delay = self.strategy.get_delay(attempt)
        return min(uncapped_delay, self.max_delay)


class DurationRetry:
    """Time-based retry strategy that keeps retrying for a specified duration.

    Instead of a fixed number of attempts, retries until the total elapsed time
    exceeds the duration. Uses exponential backoff with configurable max delay.
    """

    def __init__(
        self,
        *,
        duration: float,
        initial_delay: float = 0.1,
        backoff: float = 1.5,
        max_delay: float = 5.0,
    ):
        """Initialize duration-based retry strategy.

        Args:
            duration: Total duration in seconds to keep retrying
            initial_delay: Starting delay in seconds (default: 0.1)
            backoff: Multiplier for delay after each retry (default: 1.5)
            max_delay: Maximum delay between retries in seconds (default: 5.0)

        Example:
            # Retry for up to 60 seconds with exponential backoff
            retry = DurationRetry(duration=60.0, initial_delay=0.5, backoff=2.0, max_delay=10.0)
            # Delays: 0.5s, 1s, 2s, 4s, 8s, 10s, 10s, 10s... until 60s elapsed

            # Retry for 30 seconds with moderate backoff
            retry = DurationRetry(duration=30.0, initial_delay=0.1, backoff=1.5, max_delay=5.0)
        """
        self.duration = duration
        self.initial_delay = initial_delay
        self.backoff = backoff
        self.max_delay = max_delay
        # Set attempts to a very high number since we're duration-based
        # The actual retry logic will check elapsed time instead
        self.attempts = 999999
        self._start_time: float | None = None
        self._elapsed_time: float = 0.0

    def reset(self) -> None:
        """Reset the timer. Call this at the start of a new request cycle."""
        import time

        self._start_time = time.time()
        self._elapsed_time = 0.0

    def should_retry(self) -> bool:
        """Check if we should continue retrying based on elapsed time.

        Returns:
            True if elapsed time is less than duration, False otherwise
        """
        import time

        if self._start_time is None:
            self.reset()
            return True

        self._elapsed_time = time.time() - self._start_time
        return self._elapsed_time < self.duration

    def get_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff up to max_delay.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds for this attempt
        """
        exponential_delay = self.initial_delay * (self.backoff**attempt)
        return min(exponential_delay, self.max_delay)
