"""Comprehensive tests for encoding utilities."""

from utils import (
    base64_decode,
    base64_encode,
    defang,
    fang,
    html_decode,
    html_encode,
    url_decode,
    url_encode,
)


class TestBase64:
    """Test base64 encoding/decoding."""

    def test_base64_encode_decode(self):
        """Test base64 encode and decode."""
        text = "hello world"
        encoded = base64_encode(text)
        decoded = base64_decode(encoded)
        assert decoded == text

    def test_base64_encode_bytes(self):
        """Test base64 encode with bytes."""
        data = b"hello"
        encoded = base64_encode(data)
        assert isinstance(encoded, str)


class TestURL:
    """Test URL encoding/decoding."""

    def test_url_encode_decode(self):
        """Test URL encode and decode."""
        text = "hello world"
        encoded = url_encode(text)
        assert encoded == "hello%20world"
        decoded = url_decode(encoded)
        assert decoded == text


class TestHTML:
    """Test HTML encoding/decoding."""

    def test_html_encode_decode(self):
        """Test HTML encode and decode."""
        text = "<div>Hello</div>"
        encoded = html_encode(text)
        assert "&lt;" in encoded
        assert "&gt;" in encoded
        decoded = html_decode(encoded)
        assert decoded == text


class TestFangDefang:
    """Test fang and defang functions."""

    def test_defang(self):
        """Test defang function."""
        result = defang("example.com")
        assert result == "example[.]com"

    def test_fang(self):
        """Test fang function."""
        result = fang("example[.]com")
        assert result == "example.com"

    def test_fang_roundtrip(self):
        """Test fang/defang roundtrip."""
        original = "example.com"
        defanged = defang(original)
        fanged = fang(defanged)
        assert fanged == original
