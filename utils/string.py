import hashlib
import re
import textwrap


class String:
    """Static utility class for string operations."""

    @staticmethod
    def truncate(text: str, *, length: int, suffix: str = "...") -> str:
        """Truncate string to specified length, adding suffix if truncated.

        Examples:
            >>> String.truncate("Hello World", length=5)
            'He...'
            >>> String.truncate("Hi", length=5)
            'Hi'
        """
        if length < 0:
            raise ValueError("length must be >= 0")
        if len(text) <= length:
            return text
        if length == 0:
            return ""
        if len(suffix) >= length:
            return suffix[:length]
        head = length - len(suffix)
        return text[:head] + suffix

    @staticmethod
    def truncate_words(text: str, *, count: int, suffix: str = "...") -> str:
        """Truncate string to specified word count, adding suffix if truncated.

        Examples:
            >>> String.truncate_words("Hello World from Python", count=2)
            'Hello World...'
        """
        words = text.split()
        if len(words) <= count:
            return text
        truncated = " ".join(words[:count])
        return truncated + suffix

    @staticmethod
    def slug(text: str) -> str:
        """Convert string to URL-friendly slug format.

        Examples:
            >>> String.slug("Hello World!")
            'hello-world'
        """
        result = text.lower()
        result = re.sub(r"[^\w\s-]", "", result)  # Remove non-word chars except spaces and hyphens
        result = re.sub(r"[-\s]+", "-", result)  # Replace spaces/hyphens with single hyphen
        return result.strip("-")

    @staticmethod
    def camel_case(text: str) -> str:
        """Convert string to camelCase format.

        Examples:
            >>> String.camel_case("hello world")
            'helloWorld'
        """
        words = text.split()
        if not words:
            return ""
        return words[0].lower() + "".join(word.capitalize() for word in words[1:])

    @staticmethod
    def snake_case(text: str) -> str:
        """Convert string to snake_case format.

        Examples:
            >>> String.snake_case("Hello World")
            'hello_world'
            >>> String.snake_case("helloWorld")
            'hello_world'
        """
        s = text.strip()
        s = re.sub(r"[^\w]+", "_", s)  # Replace non-word chars with underscores
        s = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", s)  # Insert underscore before capitals
        s = s.lower()
        s = re.sub(r"_+", "_", s).strip("_")  # Consolidate multiple underscores
        return s

    @staticmethod
    def kebab_case(text: str) -> str:
        """Convert string to kebab-case format."""
        return String.slug(text)

    @staticmethod
    def title_case(text: str) -> str:
        """Convert string to Title Case format."""
        return text.title()

    @staticmethod
    def reverse(text: str) -> str:
        """Reverse the characters in a string.

        Examples:
            >>> String.reverse("hello")
            'olleh'
        """
        return text[::-1]

    @staticmethod
    def remove_whitespace(text: str) -> str:
        """Remove all whitespace from string.

        Examples:
            >>> String.remove_whitespace("hello world")
            'helloworld'
        """
        return "".join(text.split())

    @staticmethod
    def pad_left(text: str, *, width: int, fillchar: str = " ") -> str:
        """Pad string on the left to specified width.

        Examples:
            >>> String.pad_left("7", width=3, fillchar="0")
            '007'
        """
        return text.rjust(width, fillchar)

    @staticmethod
    def pad_right(text: str, *, width: int, fillchar: str = " ") -> str:
        """Pad string on the right to specified width."""
        return text.ljust(width, fillchar)

    @staticmethod
    def pad_center(text: str, *, width: int, fillchar: str = " ") -> str:
        """Center string within specified width with padding."""
        return text.center(width, fillchar)

    @staticmethod
    def remove_prefix(text: str, *, prefix: str) -> str:
        """Remove prefix from string if present.

        Examples:
            >>> String.remove_prefix("hello world", prefix="hello ")
            'world'
        """
        if text.startswith(prefix):
            return text[len(prefix) :]
        return text

    @staticmethod
    def remove_suffix(text: str, *, suffix: str) -> str:
        """Remove suffix from string if present.

        Examples:
            >>> String.remove_suffix("hello.txt", suffix=".txt")
            'hello'
        """
        if not suffix or not text.endswith(suffix):
            return text
        return text[: -len(suffix)]

    @staticmethod
    def wrap(text: str, *, width: int) -> list[str]:
        """Wrap text to specified line width.

        Examples:
            >>> String.wrap("hello world from python", width=10)
            ['hello', 'world from', 'python']
        """
        return textwrap.wrap(text, width)

    @staticmethod
    def is_email(text: str) -> bool:
        """Check if string is a valid email address."""
        # Basic email pattern: local@domain.tld
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, text))

    @staticmethod
    def is_url(text: str) -> bool:
        """Check if string is a valid HTTP/HTTPS URL."""
        # Matches http:// or https:// URLs
        pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        return bool(re.match(pattern, text))

    @staticmethod
    def extract_emails(text: str) -> list[str]:
        """Extract all email addresses from string.

        Examples:
            >>> String.extract_emails("Contact us at hello@example.com or support@test.org")
            ['hello@example.com', 'support@test.org']
        """
        pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
        return re.findall(pattern, text)

    @staticmethod
    def extract_urls(text: str) -> list[str]:
        """Extract all HTTP/HTTPS URLs from string.

        Examples:
            >>> String.extract_urls("Visit https://example.com or http://test.org")
            ['https://example.com', 'http://test.org']
        """
        pattern = r"https?://[^\s/$.?#].[^\s]*"
        return re.findall(pattern, text)

    @staticmethod
    def hash(text: str, *, algorithm: str = "sha256") -> str:
        """Generate cryptographic hash of string.

        Examples:
            >>> String.hash("hello")
            '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
        """
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(text.encode("utf-8"))
        return hash_obj.hexdigest()
