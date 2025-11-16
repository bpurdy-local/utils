import random
import secrets
import string
import uuid
from typing import Any


class Random:
    """Static utility class for random value generation."""

    @staticmethod
    def string(*, length: int = 8, chars: str | None = None) -> str:
        """Generate random string of specified length.

        Examples:
            >>> result = Random.string(length=10)
            >>> len(result)
            10

            >>> result = Random.string(length=5, chars='01')
            >>> all(c in '01' for c in result)
            True
        """
        if chars is None:
            chars = string.ascii_letters + string.digits
        # Use secrets module for cryptographically strong randomness
        return "".join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def int(*, min_val: int = 0, max_val: int = 100) -> int:
        """Generate random integer in specified range.

        Examples:
            >>> result = Random.int(min_val=1, max_val=10)
            >>> 1 <= result <= 10
            True
        """
        return random.randint(min_val, max_val)

    @staticmethod
    def float(*, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Generate random float in specified range.

        Examples:
            >>> result = Random.float(min_val=0.0, max_val=1.0)
            >>> 0.0 <= result <= 1.0
            True
        """
        return random.uniform(min_val, max_val)

    @staticmethod
    def shuffle(items: list) -> list:
        """Shuffle list items randomly.

        Examples:
            >>> result = Random.shuffle([1, 2, 3, 4, 5])
            >>> len(result)
            5
            >>> set(result) == {1, 2, 3, 4, 5}
            True
        """
        result = list(items)
        random.shuffle(result)
        return result

    @staticmethod
    def sample(items: list, *, k: int) -> list:  # type: ignore[misc]
        """Select k random items from list without replacement.

        Examples:
            >>> result = Random.sample([1, 2, 3, 4, 5], k=3)
            >>> len(result)
            3
            >>> all(item in [1, 2, 3, 4, 5] for item in result)
            True
        """
        return random.sample(items, k)

    @staticmethod
    def choice(items: list) -> Any:
        """Select single random item from list.

        Examples:
            >>> result = Random.choice([1, 2, 3, 4, 5])
            >>> result in [1, 2, 3, 4, 5]
            True
        """
        return random.choice(items)

    @staticmethod
    def uuid4() -> str:
        """Generate random UUID4 string.

        Examples:
            >>> result = Random.uuid4()
            >>> len(result)
            36
            >>> result.count('-')
            4
        """
        return str(uuid.uuid4())

    @staticmethod
    def uuid1() -> str:
        """Generate UUID1 string based on host and time.

        Examples:
            >>> result = Random.uuid1()
            >>> len(result)
            36
            >>> result.count('-')
            4
        """
        return str(uuid.uuid1())

    @staticmethod
    def uuid_string() -> str:
        """Generate random UUID string (alias for uuid4).

        Examples:
            >>> result = Random.uuid_string()
            >>> len(result)
            36
            >>> result.count('-')
            4
        """
        return Random.uuid4()
