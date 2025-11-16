"""Decoding utility class."""

import base64
import html
import urllib.parse


class Decode:
    """Static utility class for decoding operations."""

    @staticmethod
    def base64(encoded: str) -> str:
        """Decode base64 string.

        Examples:
            >>> Decode.base64("aGVsbG8=")
            'hello'
        """
        return base64.b64decode(encoded).decode("utf-8")

    @staticmethod
    def url(encoded: str) -> str:
        """URL decode string.

        Examples:
            >>> Decode.url("hello%20world")
            'hello world'
        """
        return urllib.parse.unquote(encoded)

    @staticmethod
    def html(encoded: str) -> str:
        """HTML decode string (unescape HTML entities).

        Examples:
            >>> Decode.html("&lt;div&gt;")
            '<div>'
        """
        return html.unescape(encoded)

    @staticmethod
    def fang(text: str) -> str:
        """Fang URLs/IPs (convert defanged back to normal).

        Examples:
            >>> Decode.fang("example[.]com")
            'example.com'
            >>> Decode.fang("1.1.1[.]1")
            '1.1.1.1'
        """
        result = text.replace("[.]", ".").replace("(.)", ".").replace("[dot]", ".")
        return result
