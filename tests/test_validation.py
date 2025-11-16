"""Comprehensive tests for validation utilities."""

from utils import Validator


class TestIsEmail:
    """Test is_email function."""

    def test_is_email_valid(self):
        """Test valid email addresses."""
        assert Validator.email("user@example.com") is True
        assert Validator.email("test.email+tag@example.co.uk") is True
        assert Validator.email("user_name@example-domain.com") is True
        assert Validator.email("user123@example123.com") is True

    def test_is_email_invalid(self):
        """Test invalid email addresses."""
        assert Validator.email("invalid") is False
        assert Validator.email("user@") is False
        assert Validator.email("@example.com") is False
        assert Validator.email("user@example") is False
        assert Validator.email("user @example.com") is False
        assert Validator.email("") is False


class TestIsUrl:
    """Test is_url function."""

    def test_is_url_valid(self):
        """Test valid URLs."""
        assert Validator.url("https://example.com") is True
        assert Validator.url("http://example.com") is True
        assert Validator.url("https://example.com/path") is True
        assert Validator.url("http://example.com/path?query=value") is True

    def test_is_url_invalid(self):
        """Test invalid URLs."""
        assert Validator.url("not-a-url") is False
        assert Validator.url("example.com") is False
        assert Validator.url("ftp://example.com") is False
        assert Validator.url("") is False


class TestIsPhone:
    """Test is_phone function."""

    def test_is_phone_valid(self):
        """Test valid phone numbers."""
        assert Validator.phone("+1-555-123-4567") is True
        assert Validator.phone("5551234567") is True
        assert Validator.phone("(555) 123-4567") is True
        assert Validator.phone("+44 20 1234 5678") is True

    def test_is_phone_invalid(self):
        """Test invalid phone numbers."""
        assert Validator.phone("123") is False
        assert Validator.phone("12345") is False
        assert Validator.phone("") is False
        assert Validator.phone("abc") is False


class TestIsUuid:
    """Test is_uuid function."""

    def test_is_uuid_valid(self):
        """Test valid UUIDs."""
        assert Validator.uuid("550e8400-e29b-41d4-a716-446655440000") is True
        assert Validator.uuid("00000000-0000-0000-0000-000000000000") is True
        assert Validator.uuid("FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF") is True

    def test_is_uuid_invalid(self):
        """Test invalid UUIDs."""
        assert Validator.uuid("550e8400-e29b-41d4-a716") is False
        assert Validator.uuid("not-a-uuid") is False
        assert Validator.uuid("550e8400-e29b-41d4-a716-44665544000") is False  # Too short
        assert Validator.uuid("") is False


class TestIsCreditCard:
    """Test is_credit_card function."""

    def test_is_credit_card_valid(self):
        """Test valid credit card numbers."""
        # Valid test card numbers (Luhn algorithm)
        assert Validator.credit_card("4532015112830366") is True
        assert Validator.credit_card("4532 0151 1283 0366") is True
        assert Validator.credit_card("4532-0151-1283-0366") is True

    def test_is_credit_card_invalid(self):
        """Test invalid credit card numbers."""
        assert Validator.credit_card("1234567890123456") is False  # Invalid Luhn
        assert Validator.credit_card("123") is False  # Too short
        assert Validator.credit_card("") is False
        assert Validator.credit_card("abcdefghijklmnop") is False


class TestIsHexColor:
    """Test is_hex_color function."""

    def test_is_hex_color_valid(self):
        """Test valid hex colors."""
        assert Validator.hex_color("#ff0000") is True
        assert Validator.hex_color("#FF0000") is True
        assert Validator.hex_color("#fff") is True
        assert Validator.hex_color("#FFF") is True
        assert Validator.hex_color("#000000") is True

    def test_is_hex_color_invalid(self):
        """Test invalid hex colors."""
        assert Validator.hex_color("ff0000") is False  # Missing #
        assert Validator.hex_color("#gg0000") is False  # Invalid character
        assert Validator.hex_color("#ff00") is False  # Wrong length
        assert Validator.hex_color("#ff00000") is False  # Wrong length
        assert Validator.hex_color("") is False


class TestIsIpv4:
    """Test is_ipv4 function."""

    def test_is_ipv4_valid(self):
        """Test valid IPv4 addresses."""
        assert Validator.ipv4("192.168.1.1") is True
        assert Validator.ipv4("0.0.0.0") is True
        assert Validator.ipv4("255.255.255.255") is True
        assert Validator.ipv4("127.0.0.1") is True

    def test_is_ipv4_invalid(self):
        """Test invalid IPv4 addresses."""
        assert Validator.ipv4("999.999.999.999") is False  # Out of range
        assert Validator.ipv4("192.168.1") is False  # Too few parts
        assert Validator.ipv4("192.168.1.1.1") is False  # Too many parts
        assert Validator.ipv4("192.168.1.256") is False  # Out of range
        assert Validator.ipv4("") is False
        assert Validator.ipv4("not.an.ip.address") is False


class TestIsEmpty:
    """Test is_empty function."""

    def test_is_empty_none(self):
        """Test is_empty with None."""
        assert Validator.empty(None) is True

    def test_is_empty_string(self):
        """Test is_empty with empty string."""
        assert Validator.empty("") is True
        assert Validator.empty("   ") is True  # Whitespace only

    def test_is_empty_list(self):
        """Test is_empty with empty list."""
        assert Validator.empty([]) is True

    def test_is_empty_dict(self):
        """Test is_empty with empty dict."""
        assert Validator.empty({}) is True

    def test_is_empty_tuple(self):
        """Test is_empty with empty tuple."""
        assert Validator.empty(()) is True

    def test_is_empty_set(self):
        """Test is_empty with empty set."""
        assert Validator.empty(set()) is True

    def test_is_empty_not_empty(self):
        """Test is_empty with non-empty values."""
        assert Validator.empty("hello") is False
        assert Validator.empty([1, 2, 3]) is False
        assert Validator.empty({"a": 1}) is False
        assert Validator.empty(0) is False
        assert Validator.empty(False) is False


class TestIsNumeric:
    """Test is_numeric function."""

    def test_is_numeric_valid(self):
        """Test valid numeric strings."""
        assert Validator.numeric("123") is True
        assert Validator.numeric("12.34") is True
        assert Validator.numeric("-123") is True
        assert Validator.numeric("-12.34") is True
        assert Validator.numeric("0") is True
        assert Validator.numeric("0.0") is True

    def test_is_numeric_invalid(self):
        """Test invalid numeric strings."""
        assert Validator.numeric("abc") is False
        assert Validator.numeric("12.34.56") is False
        assert Validator.numeric("") is False
        assert Validator.numeric("12a34") is False


class TestIsInteger:
    """Test is_integer function."""

    def test_is_integer_valid(self):
        """Test valid integer strings."""
        assert Validator.integer("123") is True
        assert Validator.integer("-123") is True
        assert Validator.integer("0") is True
        assert Validator.integer("999999") is True

    def test_is_integer_invalid(self):
        """Test invalid integer strings."""
        assert Validator.integer("12.34") is False
        assert Validator.integer("abc") is False
        assert Validator.integer("") is False
        assert Validator.integer("12a") is False


class TestIsLatitude:
    """Test is_latitude function."""

    def test_is_latitude_valid_strict(self):
        """Test valid latitudes with strict mode (default)."""
        assert Validator.is_latitude(0) is True
        assert Validator.is_latitude(45.5) is True
        assert Validator.is_latitude(-45.5) is True
        assert Validator.is_latitude(89.9) is True
        assert Validator.is_latitude(-89.9) is True

    def test_is_latitude_boundary_strict(self):
        """Test boundary values with strict mode."""
        assert Validator.is_latitude(90) is False
        assert Validator.is_latitude(-90) is False
        assert Validator.is_latitude(89.9999) is True
        assert Validator.is_latitude(-89.9999) is True

    def test_is_latitude_valid_non_strict(self):
        """Test valid latitudes with non-strict mode."""
        assert Validator.is_latitude(90, strict=False) is True
        assert Validator.is_latitude(-90, strict=False) is True
        assert Validator.is_latitude(0, strict=False) is True
        assert Validator.is_latitude(45.5, strict=False) is True

    def test_is_latitude_invalid(self):
        """Test invalid latitudes."""
        assert Validator.is_latitude(91) is False
        assert Validator.is_latitude(-91) is False
        assert Validator.is_latitude(180) is False
        assert Validator.is_latitude(-180) is False
        assert Validator.is_latitude(91, strict=False) is False
        assert Validator.is_latitude(-91, strict=False) is False

    def test_is_latitude_string_input(self):
        """Test latitude with string input."""
        assert Validator.is_latitude("45.5") is True
        assert Validator.is_latitude("-45.5") is True
        assert Validator.is_latitude("0") is True
        assert Validator.is_latitude("90", strict=False) is True
        assert Validator.is_latitude("90") is False
        assert Validator.is_latitude("invalid") is False
        assert Validator.is_latitude("") is False


class TestIsLongitude:
    """Test is_longitude function."""

    def test_is_longitude_valid_strict(self):
        """Test valid longitudes with strict mode (default)."""
        assert Validator.is_longitude(0) is True
        assert Validator.is_longitude(-122.4) is True
        assert Validator.is_longitude(122.4) is True
        assert Validator.is_longitude(179.9) is True
        assert Validator.is_longitude(-179.9) is True

    def test_is_longitude_boundary_strict(self):
        """Test boundary values with strict mode."""
        assert Validator.is_longitude(180) is False
        assert Validator.is_longitude(-180) is False
        assert Validator.is_longitude(179.9999) is True
        assert Validator.is_longitude(-179.9999) is True

    def test_is_longitude_valid_non_strict(self):
        """Test valid longitudes with non-strict mode."""
        assert Validator.is_longitude(180, strict=False) is True
        assert Validator.is_longitude(-180, strict=False) is True
        assert Validator.is_longitude(0, strict=False) is True
        assert Validator.is_longitude(-122.4, strict=False) is True

    def test_is_longitude_invalid(self):
        """Test invalid longitudes."""
        assert Validator.is_longitude(181) is False
        assert Validator.is_longitude(-181) is False
        assert Validator.is_longitude(360) is False
        assert Validator.is_longitude(-360) is False
        assert Validator.is_longitude(181, strict=False) is False
        assert Validator.is_longitude(-181, strict=False) is False

    def test_is_longitude_string_input(self):
        """Test longitude with string input."""
        assert Validator.is_longitude("-122.4") is True
        assert Validator.is_longitude("122.4") is True
        assert Validator.is_longitude("0") is True
        assert Validator.is_longitude("180", strict=False) is True
        assert Validator.is_longitude("180") is False
        assert Validator.is_longitude("invalid") is False
        assert Validator.is_longitude("") is False


class TestIsTimezone:
    """Test is_timezone function."""

    def test_is_timezone_valid(self):
        """Test valid IANA timezone identifiers."""
        assert Validator.is_timezone("America/New_York") is True
        assert Validator.is_timezone("UTC") is True
        assert Validator.is_timezone("Europe/London") is True
        assert Validator.is_timezone("Asia/Tokyo") is True
        assert Validator.is_timezone("Australia/Sydney") is True
        assert Validator.is_timezone("America/Los_Angeles") is True

    def test_is_timezone_invalid(self):
        """Test invalid timezone identifiers."""
        assert Validator.is_timezone("Invalid/Timezone") is False
        assert Validator.is_timezone("") is False
        assert Validator.is_timezone("America/Invalid_City") is False
        assert Validator.is_timezone("Not_A_Timezone") is False
        assert Validator.is_timezone("XYZ") is False
        assert Validator.is_timezone("123") is False


class TestIsCoordinates:
    """Test is_coordinates function."""

    def test_is_coordinates_valid_strict(self):
        """Test valid coordinate pairs with strict mode."""
        assert Validator.is_coordinates(40.7128, -74.0060) is True  # NYC
        assert Validator.is_coordinates(51.5074, -0.1278) is True  # London
        assert Validator.is_coordinates(35.6762, 139.6503) is True  # Tokyo
        assert Validator.is_coordinates(0, 0) is True  # Null Island

    def test_is_coordinates_valid_non_strict(self):
        """Test valid coordinate pairs with non-strict mode."""
        assert Validator.is_coordinates(90, 180, strict=False) is True
        assert Validator.is_coordinates(-90, -180, strict=False) is True
        assert Validator.is_coordinates(0, 0, strict=False) is True

    def test_is_coordinates_boundary_strict(self):
        """Test boundary coordinates with strict mode."""
        assert Validator.is_coordinates(90, 0) is False  # North pole
        assert Validator.is_coordinates(-90, 0) is False  # South pole
        assert Validator.is_coordinates(0, 180) is False  # Antimeridian
        assert Validator.is_coordinates(0, -180) is False  # Antimeridian

    def test_is_coordinates_invalid_latitude(self):
        """Test coordinates with invalid latitude."""
        assert Validator.is_coordinates(91, -74.0060) is False
        assert Validator.is_coordinates(-91, -74.0060) is False
        assert Validator.is_coordinates(180, 0) is False

    def test_is_coordinates_invalid_longitude(self):
        """Test coordinates with invalid longitude."""
        assert Validator.is_coordinates(40.7128, 181) is False
        assert Validator.is_coordinates(40.7128, -181) is False
        assert Validator.is_coordinates(0, 360) is False

    def test_is_coordinates_string_input(self):
        """Test coordinates with string input."""
        assert Validator.is_coordinates("40.7128", "-74.0060") is True
        assert Validator.is_coordinates("51.5074", "-0.1278") is True
        assert Validator.is_coordinates("invalid", "-74.0060") is False
        assert Validator.is_coordinates("40.7128", "invalid") is False

    def test_is_coordinates_mixed_input(self):
        """Test coordinates with mixed float/string input."""
        assert Validator.is_coordinates(40.7128, "-74.0060") is True
        assert Validator.is_coordinates("40.7128", -74.0060) is True
