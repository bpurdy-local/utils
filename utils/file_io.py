"""FileIO utility class - delegates to Path for backward compatibility."""

from pathlib import Path as PathLib
from typing import Any

from utils.path import Path


class FileIO:
    """Static utility class for file I/O operations.

    This class delegates to the Path class for all operations.
    It exists for backward compatibility and API consistency.
    """

    @staticmethod
    def read(path: str | PathLib, *, encoding: str = "utf-8") -> str:
        """Read text content from file."""
        return Path.read(path, encoding=encoding)

    @staticmethod
    def write(path: str | PathLib, *, content: str, encoding: str = "utf-8") -> int:
        """Write text content to file."""
        return Path.write(path, content=content, encoding=encoding)

    @staticmethod
    def read_lines(path: str | PathLib, *, encoding: str = "utf-8") -> list[str]:
        """Read file content as list of lines."""
        return Path.read_lines(path, encoding=encoding)

    @staticmethod
    def write_lines(path: str | PathLib, *, lines: list[str], encoding: str = "utf-8") -> int:
        """Write list of lines to file."""
        return Path.write_lines(path, lines=lines, encoding=encoding)

    @staticmethod
    def read_json(path: str | PathLib, *, encoding: str = "utf-8") -> Any:
        """Read and parse JSON from file."""
        return Path.read_json(path, encoding=encoding)

    @staticmethod
    def write_json(
        path: str | PathLib, *, data: Any, encoding: str = "utf-8", indent: int = 2
    ) -> int:
        """Write data to file as JSON."""
        return Path.write_json(path, data=data, encoding=encoding, indent=indent)

    @staticmethod
    def ensure_dir(path: str | PathLib) -> None:
        """Ensure directory exists, creating it if necessary."""
        return Path.ensure_dir(path)

    @staticmethod
    def copy(path: str | PathLib, *, destination: str | PathLib) -> PathLib:
        """Copy file or directory to destination."""
        return Path.copy(path, destination=destination)

    @staticmethod
    def move(path: str | PathLib, *, destination: str | PathLib) -> PathLib:
        """Move file or directory to destination."""
        return Path.move(path, destination=destination)
