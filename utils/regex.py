import re
from typing import Any


class Regex:
    """Static utility class for regex operations."""

    @staticmethod
    def match(pattern: str | re.Pattern[str], text: str, *, flags: int = 0) -> re.Match[str] | None:
        """Match pattern at start of string."""
        # Compile pattern if string, reuse if already compiled
        compiled = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern, flags)
        return compiled.match(text)

    @staticmethod
    def search(
        pattern: str | re.Pattern[str], text: str, *, flags: int = 0
    ) -> re.Match[str] | None:
        """Search for pattern anywhere in string."""
        compiled = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern, flags)
        return compiled.search(text)

    @staticmethod
    def findall(
        pattern: str | re.Pattern[str], text: str, *, flags: int = 0
    ) -> list[str] | list[tuple[str, ...]]:
        """Find all non-overlapping matches of pattern in string.

        Examples:
            >>> Regex.findall(r'\\d+', 'There are 12 apples and 5 oranges')
            ['12', '5']
        """
        compiled = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern, flags)
        return compiled.findall(text)

    @staticmethod
    def sub(
        pattern: str | re.Pattern[str],
        repl: str | Any,
        text: str,
        *,
        count: int = 0,
        flags: int = 0,
    ) -> str:
        """Replace matches of pattern with replacement string.

        Examples:
            >>> Regex.sub(r'\\d+', 'X', 'I have 5 cats and 3 dogs')
            'I have X cats and X dogs'
        """
        compiled = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern, flags)
        return compiled.sub(repl, text, count=count)

    @staticmethod
    def split(
        pattern: str | re.Pattern[str], text: str, *, maxsplit: int = 0, flags: int = 0
    ) -> list[str]:
        """Split string by pattern matches."""
        compiled = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern, flags)
        return compiled.split(text, maxsplit=maxsplit)

    @staticmethod
    def groups(match: re.Match[str] | None) -> tuple[str, ...] | None:
        """Extract captured groups from match object."""
        if match is None:
            return None
        return match.groups()

    @staticmethod
    def groupdict(match: re.Match[str] | None) -> dict[str, str] | None:
        """Extract named groups from match object as dictionary."""
        if match is None:
            return None
        return match.groupdict()

    @staticmethod
    def is_valid(pattern: str | re.Pattern[str], text: str, *, flags: int = 0) -> bool:
        """Check if string matches pattern."""
        compiled = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern, flags)
        return compiled.match(text) is not None
