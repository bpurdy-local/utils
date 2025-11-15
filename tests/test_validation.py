"""Comprehensive tests for validation utilities."""

from utils import (
    is_credit_card,
    is_email,
    is_empty,
    is_hex_color,
    is_integer,
    is_ipv4,
    is_numeric,
    is_phone,
    is_url,
    is_uuid,
)


class TestIsEmail:
    """Test is_email function."""

    def test_is_email_valid(self):
        """Test valid email addresses."""
        assert is_email("user@example.com") is True
        assert is_email("test.email+tag@example.co.uk") is True
        assert is_email("user_name@example-domain.com") is True
        assert is_email("user123@example123.com") is True

    def test_is_email_invalid(self):
        """Test invalid email addresses."""
        assert is_email("invalid") is False
        assert is_email("user@") is False
        assert is_email("@example.com") is False
        assert is_email("user@example") is False
        assert is_email("user @example.com") is False
        assert is_email("") is False


class TestIsUrl:
    """Test is_url function."""

    def test_is_url_valid(self):
        """Test valid URLs."""
        assert is_url("https://example.com") is True
        assert is_url("http://example.com") is True
        assert is_url("https://example.com/path") is True
        assert is_url("http://example.com/path?query=value") is True

    def test_is_url_invalid(self):
        """Test invalid URLs."""
        assert is_url("not-a-url") is False
        assert is_url("example.com") is False
        assert is_url("ftp://example.com") is False
        assert is_url("") is False


class TestIsPhone:
    """Test is_phone function."""

    def test_is_phone_valid(self):
        """Test valid phone numbers."""
        assert is_phone("+1-555-123-4567") is True
        assert is_phone("5551234567") is True
        assert is_phone("(555) 123-4567") is True
        assert is_phone("+44 20 1234 5678") is True

    def test_is_phone_invalid(self):
        """Test invalid phone numbers."""
        assert is_phone("123") is False
        assert is_phone("12345") is False
        assert is_phone("") is False
        assert is_phone("abc") is False


class TestIsUuid:
    """Test is_uuid function."""

    def test_is_uuid_valid(self):
        """Test valid UUIDs."""
        assert is_uuid("550e8400-e29b-41d4-a716-446655440000") is True
        assert is_uuid("00000000-0000-0000-0000-000000000000") is True
        assert is_uuid("FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF") is True

    def test_is_uuid_invalid(self):
        """Test invalid UUIDs."""
        assert is_uuid("550e8400-e29b-41d4-a716") is False
        assert is_uuid("not-a-uuid") is False
        assert is_uuid("550e8400-e29b-41d4-a716-44665544000") is False  # Too short
        assert is_uuid("") is False


class TestIsCreditCard:
    """Test is_credit_card function."""

    def test_is_credit_card_valid(self):
        """Test valid credit card numbers."""
        # Valid test card numbers (Luhn algorithm)
        assert is_credit_card("4532015112830366") is True
        assert is_credit_card("4532 0151 1283 0366") is True
        assert is_credit_card("4532-0151-1283-0366") is True

    def test_is_credit_card_invalid(self):
        """Test invalid credit card numbers."""
        assert is_credit_card("1234567890123456") is False  # Invalid Luhn
        assert is_credit_card("123") is False  # Too short
        assert is_credit_card("") is False
        assert is_credit_card("abcdefghijklmnop") is False


class TestIsHexColor:
    """Test is_hex_color function."""

    def test_is_hex_color_valid(self):
        """Test valid hex colors."""
        assert is_hex_color("#ff0000") is True
        assert is_hex_color("#FF0000") is True
        assert is_hex_color("#fff") is True
        assert is_hex_color("#FFF") is True
        assert is_hex_color("#000000") is True

    def test_is_hex_color_invalid(self):
        """Test invalid hex colors."""
        assert is_hex_color("ff0000") is False  # Missing #
        assert is_hex_color("#gg0000") is False  # Invalid character
        assert is_hex_color("#ff00") is False  # Wrong length
        assert is_hex_color("#ff00000") is False  # Wrong length
        assert is_hex_color("") is False


class TestIsIpv4:
    """Test is_ipv4 function."""

    def test_is_ipv4_valid(self):
        """Test valid IPv4 addresses."""
        assert is_ipv4("192.168.1.1") is True
        assert is_ipv4("0.0.0.0") is True
        assert is_ipv4("255.255.255.255") is True
        assert is_ipv4("127.0.0.1") is True

    def test_is_ipv4_invalid(self):
        """Test invalid IPv4 addresses."""
        assert is_ipv4("999.999.999.999") is False  # Out of range
        assert is_ipv4("192.168.1") is False  # Too few parts
        assert is_ipv4("192.168.1.1.1") is False  # Too many parts
        assert is_ipv4("192.168.1.256") is False  # Out of range
        assert is_ipv4("") is False
        assert is_ipv4("not.an.ip.address") is False


class TestIsEmpty:
    """Test is_empty function."""

    def test_is_empty_none(self):
        """Test is_empty with None."""
        assert is_empty(None) is True

    def test_is_empty_string(self):
        """Test is_empty with empty string."""
        assert is_empty("") is True
        assert is_empty("   ") is True  # Whitespace only

    def test_is_empty_list(self):
        """Test is_empty with empty list."""
        assert is_empty([]) is True

    def test_is_empty_dict(self):
        """Test is_empty with empty dict."""
        assert is_empty({}) is True

    def test_is_empty_tuple(self):
        """Test is_empty with empty tuple."""
        assert is_empty(()) is True

    def test_is_empty_set(self):
        """Test is_empty with empty set."""
        assert is_empty(set()) is True

    def test_is_empty_not_empty(self):
        """Test is_empty with non-empty values."""
        assert is_empty("hello") is False
        assert is_empty([1, 2, 3]) is False
        assert is_empty({"a": 1}) is False
        assert is_empty(0) is False
        assert is_empty(False) is False


class TestIsNumeric:
    """Test is_numeric function."""

    def test_is_numeric_valid(self):
        """Test valid numeric strings."""
        assert is_numeric("123") is True
        assert is_numeric("12.34") is True
        assert is_numeric("-123") is True
        assert is_numeric("-12.34") is True
        assert is_numeric("0") is True
        assert is_numeric("0.0") is True

    def test_is_numeric_invalid(self):
        """Test invalid numeric strings."""
        assert is_numeric("abc") is False
        assert is_numeric("12.34.56") is False
        assert is_numeric("") is False
        assert is_numeric("12a34") is False


class TestIsInteger:
    """Test is_integer function."""

    def test_is_integer_valid(self):
        """Test valid integer strings."""
        assert is_integer("123") is True
        assert is_integer("-123") is True
        assert is_integer("0") is True
        assert is_integer("999999") is True

    def test_is_integer_invalid(self):
        """Test invalid integer strings."""
        assert is_integer("12.34") is False
        assert is_integer("abc") is False
        assert is_integer("") is False
        assert is_integer("12a") is False
