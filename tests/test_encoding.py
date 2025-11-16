"""Comprehensive tests for encoding utilities."""

from utils.decode import Decode
from utils.encode import Encode


class TestEncodeBase64:
    """Test base64 encoding."""

    def test_encode_string(self):
        """Test base64 encode string."""
        text = "hello world"
        encoded = Encode.base64(text)
        assert encoded == "aGVsbG8gd29ybGQ="

    def test_encode_bytes(self):
        """Test base64 encode with bytes."""
        data = b"hello"
        encoded = Encode.base64(data)
        assert isinstance(encoded, str)
        assert encoded == "aGVsbG8="

    def test_encode_empty_string(self):
        """Test base64 encode empty string."""
        encoded = Encode.base64("")
        assert encoded == ""


class TestDecodeBase64:
    """Test base64 decoding."""

    def test_decode_string(self):
        """Test base64 decode string."""
        encoded = "aGVsbG8gd29ybGQ="
        decoded = Decode.base64(encoded)
        assert decoded == "hello world"

    def test_encode_decode_roundtrip(self):
        """Test base64 encode and decode roundtrip."""
        text = "hello world"
        encoded = Encode.base64(text)
        decoded = Decode.base64(encoded)
        assert decoded == text


class TestEncodeURL:
    """Test URL encoding."""

    def test_encode_spaces(self):
        """Test URL encode with spaces."""
        text = "hello world"
        encoded = Encode.url(text)
        assert encoded == "hello%20world"

    def test_encode_special_chars(self):
        """Test URL encode with special characters."""
        text = "hello@world.com"
        encoded = Encode.url(text)
        assert "@" not in encoded or encoded == "hello%40world.com"

    def test_encode_empty_string(self):
        """Test URL encode empty string."""
        encoded = Encode.url("")
        assert encoded == ""


class TestDecodeURL:
    """Test URL decoding."""

    def test_decode_spaces(self):
        """Test URL decode with spaces."""
        encoded = "hello%20world"
        decoded = Decode.url(encoded)
        assert decoded == "hello world"

    def test_encode_decode_roundtrip(self):
        """Test URL encode and decode roundtrip."""
        text = "hello world"
        encoded = Encode.url(text)
        decoded = Decode.url(encoded)
        assert decoded == text


class TestEncodeHTML:
    """Test HTML encoding."""

    def test_encode_tags(self):
        """Test HTML encode tags."""
        text = "<div>Hello</div>"
        encoded = Encode.html(text)
        assert "&lt;" in encoded
        assert "&gt;" in encoded
        assert encoded == "&lt;div&gt;Hello&lt;/div&gt;"

    def test_encode_ampersand(self):
        """Test HTML encode ampersand."""
        text = "A & B"
        encoded = Encode.html(text)
        assert "&amp;" in encoded

    def test_encode_quotes(self):
        """Test HTML encode quotes."""
        text = 'Say "hello"'
        encoded = Encode.html(text)
        assert "&quot;" in encoded or '"' in encoded


class TestDecodeHTML:
    """Test HTML decoding."""

    def test_decode_tags(self):
        """Test HTML decode tags."""
        encoded = "&lt;div&gt;Hello&lt;/div&gt;"
        decoded = Decode.html(encoded)
        assert decoded == "<div>Hello</div>"

    def test_decode_ampersand(self):
        """Test HTML decode ampersand."""
        encoded = "A &amp; B"
        decoded = Decode.html(encoded)
        assert decoded == "A & B"

    def test_encode_decode_roundtrip(self):
        """Test HTML encode and decode roundtrip."""
        text = "<div>Hello</div>"
        encoded = Encode.html(text)
        decoded = Decode.html(encoded)
        assert decoded == text


class TestEncodeDefang:
    """Test defang encoding."""

    def test_defang_domain(self):
        """Test defang domain."""
        result = Encode.defang("example.com")
        assert result == "example[.]com"

    def test_defang_ip(self):
        """Test defang IP address."""
        result = Encode.defang("1.1.1.1")
        assert result == "1[.]1[.]1[.]1"

    def test_defang_url(self):
        """Test defang URL."""
        result = Encode.defang("http://example.com")
        assert result == "http://example[.]com"


class TestDecodeFang:
    """Test fang decoding."""

    def test_fang_domain(self):
        """Test fang domain."""
        result = Decode.fang("example[.]com")
        assert result == "example.com"

    def test_fang_ip(self):
        """Test fang IP address."""
        result = Decode.fang("1[.]1[.]1[.]1")
        assert result == "1.1.1.1"

    def test_fang_parentheses(self):
        """Test fang with parentheses notation."""
        result = Decode.fang("example(.)com")
        assert result == "example.com"

    def test_fang_dot_word(self):
        """Test fang with [dot] notation."""
        result = Decode.fang("example[dot]com")
        assert result == "example.com"

    def test_defang_fang_roundtrip(self):
        """Test defang/fang roundtrip."""
        original = "example.com"
        defanged = Encode.defang(original)
        fanged = Decode.fang(defanged)
        assert fanged == original
