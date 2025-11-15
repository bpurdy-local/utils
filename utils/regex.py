import re
from typing import Any


class Regex:
    @staticmethod
    def match(pattern: str | re.Pattern[str], text: str, *, flags: int = 0) -> re.Match[str] | None:
        compiled = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern, flags)
        return compiled.match(text)

    @staticmethod
    def search(
        pattern: str | re.Pattern[str], text: str, *, flags: int = 0
    ) -> re.Match[str] | None:
        compiled = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern, flags)
        return compiled.search(text)

    @staticmethod
    def findall(
        pattern: str | re.Pattern[str], text: str, *, flags: int = 0
    ) -> list[str] | list[tuple[str, ...]]:
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
        compiled = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern, flags)
        return compiled.sub(repl, text, count=count)

    @staticmethod
    def split(
        pattern: str | re.Pattern[str], text: str, *, maxsplit: int = 0, flags: int = 0
    ) -> list[str]:
        compiled = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern, flags)
        return compiled.split(text, maxsplit=maxsplit)

    @staticmethod
    def groups(match: re.Match[str] | None) -> tuple[str, ...] | None:
        if match is None:
            return None
        return match.groups()

    @staticmethod
    def groupdict(match: re.Match[str] | None) -> dict[str, str] | None:
        if match is None:
            return None
        return match.groupdict()

    @staticmethod
    def is_valid(pattern: str | re.Pattern[str], text: str, *, flags: int = 0) -> bool:
        compiled = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern, flags)
        return compiled.match(text) is not None
