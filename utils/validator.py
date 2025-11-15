import re
from typing import Any


class Validator:
    @staticmethod
    def email(value: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, value))

    @staticmethod
    def url(value: str) -> bool:
        pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        return bool(re.match(pattern, value))

    @staticmethod
    def phone(value: str) -> bool:
        digits = re.sub(r"[^\d]", "", value)
        return 10 <= len(digits) <= 15

    @staticmethod
    def credit_card(value: str) -> bool:
        digits = re.sub(r"[^\d]", "", value)
        if not digits or len(digits) < 13:
            return False

        def luhn_check(card_number: str) -> bool:
            def digits_of(n: str) -> list[int]:
                return [int(d) for d in n]

            digits = digits_of(card_number)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(str(d * 2)))
            return checksum % 10 == 0

        return luhn_check(digits)

    @staticmethod
    def uuid(value: str) -> bool:
        pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        return bool(re.match(pattern, value, re.IGNORECASE))

    @staticmethod
    def hex_color(value: str) -> bool:
        pattern = r"^#([0-9a-f]{3}|[0-9a-f]{6})$"
        return bool(re.match(pattern, value, re.IGNORECASE))

    @staticmethod
    def ipv4(value: str) -> bool:
        parts = value.split(".")
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False

    @staticmethod
    def empty(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, str):
            return len(value.strip()) == 0
        if isinstance(value, (list, dict, tuple, set)):
            return len(value) == 0
        return False

    @staticmethod
    def numeric(value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def integer(value: str) -> bool:
        try:
            int(value)
            return True
        except ValueError:
            return False
