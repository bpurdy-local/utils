import re
from typing import Any


class Validator:
    """Static utility class for validation operations."""

    @staticmethod
    def email(value: str) -> bool:
        """Validate email address format.

        Examples:
            >>> Validator.email("test@example.com")
            True
            >>> Validator.email("invalid-email")
            False
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, value))

    @staticmethod
    def url(value: str) -> bool:
        """Validate URL format.

        Examples:
            >>> Validator.url("https://example.com")
            True
            >>> Validator.url("not a url")
            False
        """
        pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        return bool(re.match(pattern, value))

    @staticmethod
    def phone(value: str) -> bool:
        """Validate phone number (10-15 digits)."""
        digits = re.sub(r"[^\d]", "", value)
        return 10 <= len(digits) <= 15

    @staticmethod
    def credit_card(value: str) -> bool:
        """Validate credit card number using Luhn algorithm."""
        digits = re.sub(r"[^\d]", "", value)
        if not digits or len(digits) < 13:
            return False

        # Luhn algorithm: double every other digit from right, sum all digits
        def luhn_check(card_number: str) -> bool:
            def digits_of(n: str) -> list[int]:
                return [int(d) for d in n]

            digits = digits_of(card_number)
            odd_digits = digits[-1::-2]  # Every other digit starting from right
            even_digits = digits[-2::-2]  # Remaining digits
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(str(d * 2)))  # Double and sum digits
            return checksum % 10 == 0

        return luhn_check(digits)

    @staticmethod
    def uuid(value: str) -> bool:
        """Validate UUID format.

        Examples:
            >>> Validator.uuid("550e8400-e29b-41d4-a716-446655440000")
            True
            >>> Validator.uuid("invalid-uuid")
            False
        """
        pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        return bool(re.match(pattern, value, re.IGNORECASE))

    @staticmethod
    def hex_color(value: str) -> bool:
        """Validate hex color code format.

        Examples:
            >>> Validator.hex_color("#ff0000")
            True
            >>> Validator.hex_color("#f00")
            True
            >>> Validator.hex_color("red")
            False
        """
        pattern = r"^#([0-9a-f]{3}|[0-9a-f]{6})$"
        return bool(re.match(pattern, value, re.IGNORECASE))

    @staticmethod
    def ipv4(value: str) -> bool:
        """Validate IPv4 address format.

        Examples:
            >>> Validator.ipv4("192.168.1.1")
            True
            >>> Validator.ipv4("256.1.1.1")
            False
        """
        parts = value.split(".")
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False

    @staticmethod
    def empty(value: Any) -> bool:
        """Check if value is empty (None, empty string, empty collection)."""
        if value is None:
            return True
        if isinstance(value, str):
            return len(value.strip()) == 0
        if isinstance(value, list | dict | tuple | set):
            return len(value) == 0
        return False

    @staticmethod
    def numeric(value: str) -> bool:
        """Check if string represents a numeric value."""
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def integer(value: str) -> bool:
        """Check if string represents an integer value."""
        try:
            int(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_latitude(value: float | str, *, strict: bool = True) -> bool:
        """Validate latitude value (-90 to 90).

        Examples:
            >>> Validator.is_latitude(45.5)
            True

            >>> Validator.is_latitude(-90)
            False

            >>> Validator.is_latitude(-90, strict=False)
            True

            >>> Validator.is_latitude(91)
            False

            >>> Validator.is_latitude("45.5")
            True

            >>> Validator.is_latitude("invalid")
            False
        """
        try:
            lat = float(value)
            if strict:
                return -90 < lat < 90
            return -90 <= lat <= 90
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_longitude(value: float | str, *, strict: bool = True) -> bool:
        """Validate longitude value (-180 to 180).

        Examples:
            >>> Validator.is_longitude(-122.4)
            True

            >>> Validator.is_longitude(180)
            False

            >>> Validator.is_longitude(180, strict=False)
            True

            >>> Validator.is_longitude(181)
            False

            >>> Validator.is_longitude("-122.4")
            True
        """
        try:
            lon = float(value)
            if strict:
                return -180 < lon < 180
            return -180 <= lon <= 180
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_timezone(value: str) -> bool:
        """Validate IANA timezone identifier.

        Examples:
            >>> Validator.is_timezone("America/New_York")
            True

            >>> Validator.is_timezone("UTC")
            True

            >>> Validator.is_timezone("Europe/London")
            True

            >>> Validator.is_timezone("Invalid/Timezone")
            False

            >>> Validator.is_timezone("EST")
            False
        """
        try:
            from zoneinfo import ZoneInfo

            # Try to create a ZoneInfo object
            ZoneInfo(value)
            return True
        except Exception:
            return False

    @staticmethod
    def is_coordinates(
        latitude: float | str, longitude: float | str, *, strict: bool = True
    ) -> bool:
        """Validate coordinate pair (latitude, longitude).

        Examples:
            >>> Validator.is_coordinates(40.7128, -74.0060)
            True

            >>> Validator.is_coordinates("40.7128", "-74.0060")
            True

            >>> Validator.is_coordinates(91, -74.0060)
            False

            >>> Validator.is_coordinates(40.7128, 181)
            False
        """
        return Validator.is_latitude(latitude, strict=strict) and Validator.is_longitude(
            longitude, strict=strict
        )
