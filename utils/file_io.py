from __future__ import annotations

from pathlib import Path as PathLib
from typing import Any

from utils.path import Path


class FileIO:
    @staticmethod
    def read(filepath: str | PathLib, *, encoding: str = "utf-8") -> str:
        return Path.read(filepath, encoding=encoding)

    @staticmethod
    def write(filepath: str | PathLib, *, content: str, encoding: str = "utf-8") -> int:
        return Path.write(filepath, content=content, encoding=encoding)

    @staticmethod
    def read_lines(filepath: str | PathLib, *, encoding: str = "utf-8") -> list[str]:
        return Path.read_lines(filepath, encoding=encoding)

    @staticmethod
    def write_lines(filepath: str | PathLib, *, lines: list[str], encoding: str = "utf-8") -> int:
        return Path.write_lines(filepath, lines=lines, encoding=encoding)

    @staticmethod
    def read_json(filepath: str | PathLib, *, encoding: str = "utf-8") -> Any:
        return Path.read_json(filepath, encoding=encoding)

    @staticmethod
    def write_json(
        filepath: str | PathLib, *, data: Any, encoding: str = "utf-8", indent: int = 2
    ) -> int:
        return Path.write_json(filepath, data=data, encoding=encoding, indent=indent)

    @staticmethod
    def ensure_dir(dirpath: str | PathLib) -> None:
        Path.ensure_dir(dirpath)

    @staticmethod
    def copy(source: str | PathLib, *, destination: str | PathLib) -> PathLib:
        return Path.copy(source, destination=destination)

    @staticmethod
    def move(source: str | PathLib, *, destination: str | PathLib) -> PathLib:
        return Path.move(source, destination=destination)
