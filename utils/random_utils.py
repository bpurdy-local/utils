import random
import secrets
import string
import uuid
from typing import Any


class Random:
    @staticmethod
    def string(*, length: int = 8, chars: str | None = None) -> str:
        if chars is None:
            chars = string.ascii_letters + string.digits
        return "".join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def int(*, min_val: int = 0, max_val: int = 100) -> int:
        return random.randint(min_val, max_val)

    @staticmethod
    def float(*, min_val: float = 0.0, max_val: float = 1.0) -> float:
        return random.uniform(min_val, max_val)

    @staticmethod
    def shuffle(items: list) -> list:
        result = list(items)
        random.shuffle(result)
        return result

    @staticmethod
    def sample(items: list, *, k: int) -> list:  # type: ignore[misc]
        return random.sample(items, k)

    @staticmethod
    def choice(items: list) -> Any:
        return random.choice(items)

    @staticmethod
    def uuid4() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def uuid1() -> str:
        return str(uuid.uuid1())

    @staticmethod
    def uuid_string() -> str:
        return Random.uuid4()
