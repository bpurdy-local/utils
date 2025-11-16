from __future__ import annotations

from pathlib import Path as PathLib
from typing import Any

from utils.path import Path


class FileIO:
    """Static utility class for file I/O operations (delegates to Path class)."""

    @staticmethod
    def read(filepath: str | PathLib, *, encoding: str = "utf-8") -> str:
        """Read text content from file."""
        return Path.read(filepath, encoding=encoding)

    @staticmethod
    def write(filepath: str | PathLib, *, content: str, encoding: str = "utf-8") -> int:
        """Write text content to file."""
        return Path.write(filepath, content=content, encoding=encoding)

    @staticmethod
    def read_lines(filepath: str | PathLib, *, encoding: str = "utf-8") -> list[str]:
        """Read file content as list of lines."""
        return Path.read_lines(filepath, encoding=encoding)

    @staticmethod
    def write_lines(filepath: str | PathLib, *, lines: list[str], encoding: str = "utf-8") -> int:
        """Write list of lines to file."""
        return Path.write_lines(filepath, lines=lines, encoding=encoding)

    @staticmethod
    def read_json(filepath: str | PathLib, *, encoding: str = "utf-8") -> Any:
        """Read and parse JSON from file."""
        return Path.read_json(filepath, encoding=encoding)

    @staticmethod
    def write_json(
        filepath: str | PathLib, *, data: Any, encoding: str = "utf-8", indent: int = 2
    ) -> int:
        """Write data to file as JSON."""
        return Path.write_json(filepath, data=data, encoding=encoding, indent=indent)

    @staticmethod
    def ensure_dir(dirpath: str | PathLib) -> None:
        """Ensure directory exists, creating it if necessary."""
        Path.ensure_dir(dirpath)

    @staticmethod
    def copy(source: str | PathLib, *, destination: str | PathLib) -> PathLib:
        """Copy file or directory to destination."""
        return Path.copy(source, destination=destination)

    @staticmethod
    def move(source: str | PathLib, *, destination: str | PathLib) -> PathLib:
        """Move file or directory to destination."""
        return Path.move(source, destination=destination)
