import hashlib
import random
import secrets
import string


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
    def hex(*, length: int = 32) -> str:
        """Generate random hexadecimal string.

        Examples:
            >>> result = Random.hex(length=32)
            >>> len(result)
            32
            >>> all(c in '0123456789abcdef' for c in result)
            True
        """
        return secrets.token_hex(length // 2)

    @staticmethod
    def md5() -> str:
        """Generate random MD5 hash.

        Examples:
            >>> result = Random.md5()
            >>> len(result)
            32
        """
        random_bytes = secrets.token_bytes(16)
        return hashlib.md5(random_bytes).hexdigest()

    @staticmethod
    def sha1() -> str:
        """Generate random SHA-1 hash.

        Examples:
            >>> result = Random.sha1()
            >>> len(result)
            40
        """
        random_bytes = secrets.token_bytes(20)
        return hashlib.sha1(random_bytes).hexdigest()

    @staticmethod
    def sha256() -> str:
        """Generate random SHA-256 hash.

        Examples:
            >>> result = Random.sha256()
            >>> len(result)
            64
        """
        random_bytes = secrets.token_bytes(32)
        return hashlib.sha256(random_bytes).hexdigest()

    @staticmethod
    def sha512() -> str:
        """Generate random SHA-512 hash.

        Examples:
            >>> result = Random.sha512()
            >>> len(result)
            128
        """
        random_bytes = secrets.token_bytes(64)
        return hashlib.sha512(random_bytes).hexdigest()
