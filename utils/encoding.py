"""Encoding and decoding utility functions."""

import base64
import html
import urllib.parse


def base64_encode(data: str | bytes) -> str:
    """Encode string or bytes to base64.

    Args:
        data: String or bytes to encode

    Returns:
        Base64 encoded string

    Examples:
        >>> base64_encode("hello")
        'aGVsbG8='
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    return base64.b64encode(data).decode("utf-8")


def base64_decode(encoded: str) -> str:
    """Decode base64 string.

    Args:
        encoded: Base64 encoded string

    Returns:
        Decoded string

    Examples:
        >>> base64_decode("aGVsbG8=")
        'hello'
    """
    return base64.b64decode(encoded).decode("utf-8")


def url_encode(text: str) -> str:
    """URL encode string.

    Args:
        text: String to encode

    Returns:
        URL encoded string

    Examples:
        >>> url_encode("hello world")
        'hello%20world'
    """
    return urllib.parse.quote(text)


def url_decode(encoded: str) -> str:
    """URL decode string.

    Args:
        encoded: URL encoded string

    Returns:
        Decoded string

    Examples:
        >>> url_decode("hello%20world")
        'hello world'
    """
    return urllib.parse.unquote(encoded)


def html_encode(text: str) -> str:
    """HTML encode string (escape HTML entities).

    Args:
        text: String to encode

    Returns:
        HTML encoded string

    Examples:
        >>> html_encode("<div>")
        '&lt;div&gt;'
    """
    return html.escape(text)


def html_decode(encoded: str) -> str:
    """HTML decode string (unescape HTML entities).

    Args:
        encoded: HTML encoded string

    Returns:
        Decoded string

    Examples:
        >>> html_decode("&lt;div&gt;")
        '<div>'
    """
    return html.unescape(encoded)


def fang(text: str) -> str:
    """Fang URLs/IPs (convert defanged back to normal).

    Args:
        text: Defanged text

    Returns:
        Fanged text

    Examples:
        >>> fang("example[.]com")
        'example.com'
        >>> fang("1.1.1[.]1")
        '1.1.1.1'
    """
    result = text.replace("[.]", ".").replace("(.)", ".").replace("[dot]", ".")
    return result


def defang(text: str) -> str:
    """Defang URLs/IPs (make safe for display).

    Args:
        text: Text to defang

    Returns:
        Defanged text

    Examples:
        >>> defang("example.com")
        'example[.]com'
        >>> defang("1.1.1.1")
        '1.1.1[.]1'
    """
    # Simple defanging - replace dots with [.]
    return text.replace(".", "[.]")
