from __future__ import annotations

import json
import shutil
from pathlib import Path as PathLib
from typing import Any


class Path:
    """Static utility class for filesystem path operations."""

    @staticmethod
    def exists(path: str | PathLib) -> bool:
        """Check if a path exists (file or directory).

        Args:
            path: Path to check

        Returns:
            True if path exists, False otherwise

        Examples:
            >>> Path.exists("/tmp/test.txt")
            False

            >>> Path.write("/tmp/test.txt", content="hello")
            5
            >>> Path.exists("/tmp/test.txt")
            True

            >>> Path.exists("/usr/bin")
            True
        """
        return PathLib(path).exists()

    @staticmethod
    def read(path: str | PathLib, *, encoding: str = "utf-8") -> str:
        """Read text content from file."""
        return PathLib(path).read_text(encoding=encoding)

    @staticmethod
    def write(path: str | PathLib, *, content: str, encoding: str = "utf-8") -> int:
        """Write text content to file."""
        return PathLib(path).write_text(content, encoding=encoding)

    @staticmethod
    def read_lines(path: str | PathLib, *, encoding: str = "utf-8") -> list[str]:
        """Read file content as list of lines."""
        return PathLib(path).read_text(encoding=encoding).splitlines()

    @staticmethod
    def write_lines(path: str | PathLib, *, lines: list[str], encoding: str = "utf-8") -> int:
        """Write list of lines to file."""
        return PathLib(path).write_text("\n".join(lines), encoding=encoding)

    @staticmethod
    def read_json(path: str | PathLib, *, encoding: str = "utf-8") -> Any:
        """Read and parse JSON from file."""
        return json.loads(PathLib(path).read_text(encoding=encoding))

    @staticmethod
    def write_json(
        path: str | PathLib, *, data: Any, encoding: str = "utf-8", indent: int = 2
    ) -> int:
        """Write data to file as JSON."""
        return PathLib(path).write_text(json.dumps(data, indent=indent), encoding=encoding)

    @staticmethod
    def extension(path: str | PathLib) -> str:
        """Get file extension including the dot.

        Examples:
            >>> Path.extension("file.txt")
            '.txt'
        """
        return PathLib(path).suffix

    @staticmethod
    def get_stem(path: str | PathLib) -> str:
        """Get filename without extension.

        Examples:
            >>> Path.get_stem("file.txt")
            'file'
        """
        return PathLib(path).stem

    @staticmethod
    def rm(path: str | PathLib, *, recursive: bool = False) -> None:
        """Remove file or directory."""
        p = PathLib(path)
        if p.is_dir():
            if recursive:
                shutil.rmtree(p)
            else:
                p.rmdir()
        else:
            p.unlink()

    @staticmethod
    def copy(path: str | PathLib, *, destination: str | PathLib) -> PathLib:
        """Copy file or directory to destination."""
        p = PathLib(path)
        dest = PathLib(destination)
        if p.is_dir():
            shutil.copytree(p, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(p, dest)
        return dest

    @staticmethod
    def move(path: str | PathLib, *, destination: str | PathLib) -> PathLib:
        """Move file or directory to destination."""
        p = PathLib(path)
        dest = PathLib(destination)
        shutil.move(str(p), str(dest))
        return dest

    @staticmethod
    def size(path: str | PathLib) -> int:
        """Get file size in bytes."""
        return PathLib(path).stat().st_size

    @staticmethod
    def ensure_dir(path: str | PathLib) -> None:
        """Ensure directory exists, creating it if necessary."""
        p = PathLib(path)
        if p.is_dir():
            return
        p.mkdir(parents=True, exist_ok=True)
