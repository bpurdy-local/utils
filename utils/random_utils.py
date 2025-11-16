import random
import secrets
import string
import uuid
from typing import Any


class Random:
    """Static utility class for random value generation."""

    @staticmethod
    def string(*, length: int = 8, chars: str | None = None) -> str:
        """Generate random string of specified length."""
        if chars is None:
            chars = string.ascii_letters + string.digits
        # Use secrets module for cryptographically strong randomness
        return "".join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def int(*, min_val: int = 0, max_val: int = 100) -> int:
        """Generate random integer in specified range."""
        return random.randint(min_val, max_val)

    @staticmethod
    def float(*, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Generate random float in specified range."""
        return random.uniform(min_val, max_val)

    @staticmethod
    def shuffle(items: list) -> list:
        """Shuffle list items randomly."""
        result = list(items)
        random.shuffle(result)
        return result

    @staticmethod
    def sample(items: list, *, k: int) -> list:  # type: ignore[misc]
        """Select k random items from list without replacement."""
        return random.sample(items, k)

    @staticmethod
    def choice(items: list) -> Any:
        """Select single random item from list."""
        return random.choice(items)

    @staticmethod
    def uuid4() -> str:
        """Generate random UUID4 string."""
        return str(uuid.uuid4())

    @staticmethod
    def uuid1() -> str:
        """Generate UUID1 string based on host and time."""
        return str(uuid.uuid1())

    @staticmethod
    def uuid_string() -> str:
        """Generate random UUID string (alias for uuid4)."""
        return Random.uuid4()
