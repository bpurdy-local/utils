"""Encoding utility class."""

import base64
import html
import urllib.parse


class Encode:
    """Static utility class for encoding operations."""

    @staticmethod
    def base64(data: str | bytes) -> str:
        """Encode string or bytes to base64.

        Args:
            data: String or bytes to encode

        Returns:
            Base64 encoded string

        Examples:
            >>> Encode.base64("hello")
            'aGVsbG8='
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        return base64.b64encode(data).decode("utf-8")

    @staticmethod
    def url(text: str) -> str:
        """URL encode string.

        Args:
            text: String to encode

        Returns:
            URL encoded string

        Examples:
            >>> Encode.url("hello world")
            'hello%20world'
        """
        return urllib.parse.quote(text)

    @staticmethod
    def html(text: str) -> str:
        """HTML encode string (escape HTML entities).

        Args:
            text: String to encode

        Returns:
            HTML encoded string

        Examples:
            >>> Encode.html("<div>")
            '&lt;div&gt;'
        """
        return html.escape(text)

    @staticmethod
    def defang(text: str) -> str:
        """Defang URLs/IPs (make safe for display).

        Args:
            text: Text to defang

        Returns:
            Defanged text

        Examples:
            >>> Encode.defang("example.com")
            'example[.]com'
            >>> Encode.defang("1.1.1.1")
            '1.1.1[.]1'
        """
        return text.replace(".", "[.]")
