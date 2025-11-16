import functools
import threading
import time
from collections.abc import Callable
from typing import Any


class Decorators:
    """Static utility class for function decorators."""

    @staticmethod
    def debounce(*, delay: float) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Delay function execution until after delay seconds of inactivity."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            timer: threading.Timer | None = None

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                nonlocal timer
                if timer is not None:
                    timer.cancel()
                timer = threading.Timer(delay, func, args=args, kwargs=kwargs)
                timer.start()

            return wrapper

        return decorator

    @staticmethod
    def throttle(*, delay: float) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Limit function execution to once per delay seconds."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            last_called: float | None = None

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                nonlocal last_called
                now = time.time()
                if last_called is None or now - last_called >= delay:
                    last_called = now
                    return func(*args, **kwargs)
                return None

            return wrapper

        return decorator

    @staticmethod
    def retry(
        *,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple[type[Exception], ...] = (Exception,),
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Retry function on exception with exponential backoff."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                current_delay = delay
                last_exception = None
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            time.sleep(current_delay)
                            current_delay *= backoff  # Exponential backoff
                        else:
                            raise
                if last_exception:
                    raise last_exception
                raise RuntimeError("Function failed after all retries")

            return wrapper

        return decorator

    @staticmethod
    def memoize(func: Callable[..., Any]) -> Callable[..., Any]:
        """Cache function results based on arguments."""
        cache: dict[tuple[Any, ...], Any] = {}

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (args, tuple(sorted(kwargs.items())))
            if key not in cache:
                cache[key] = func(*args, **kwargs)
            return cache[key]

        return wrapper

    @staticmethod
    def once(func: Callable[..., Any]) -> Callable[..., Any]:
        """Ensure function is called only once, caching the result."""
        called = False
        result = None

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal called, result
            if not called:
                called = True
                result = func(*args, **kwargs)
            return result

        return wrapper
