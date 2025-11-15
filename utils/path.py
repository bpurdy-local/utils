from __future__ import annotations

import json
import shutil
from pathlib import Path as PathLib
from typing import Any


class Path:
    @staticmethod
    def read(path: str | PathLib, *, encoding: str = "utf-8") -> str:
        return PathLib(path).read_text(encoding=encoding)

    @staticmethod
    def write(path: str | PathLib, *, content: str, encoding: str = "utf-8") -> int:
        return PathLib(path).write_text(content, encoding=encoding)

    @staticmethod
    def read_lines(path: str | PathLib, *, encoding: str = "utf-8") -> list[str]:
        return PathLib(path).read_text(encoding=encoding).splitlines()

    @staticmethod
    def write_lines(path: str | PathLib, *, lines: list[str], encoding: str = "utf-8") -> int:
        return PathLib(path).write_text("\n".join(lines), encoding=encoding)

    @staticmethod
    def read_json(path: str | PathLib, *, encoding: str = "utf-8") -> Any:
        return json.loads(PathLib(path).read_text(encoding=encoding))

    @staticmethod
    def write_json(
        path: str | PathLib, *, data: Any, encoding: str = "utf-8", indent: int = 2
    ) -> int:
        return PathLib(path).write_text(json.dumps(data, indent=indent), encoding=encoding)

    @staticmethod
    def extension(path: str | PathLib) -> str:
        return PathLib(path).suffix

    @staticmethod
    def get_stem(path: str | PathLib) -> str:
        return PathLib(path).stem

    @staticmethod
    def rm(path: str | PathLib, *, recursive: bool = False) -> None:
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
        p = PathLib(path)
        dest = PathLib(destination)
        if p.is_dir():
            shutil.copytree(p, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(p, dest)
        return dest

    @staticmethod
    def move(path: str | PathLib, *, destination: str | PathLib) -> PathLib:
        p = PathLib(path)
        dest = PathLib(destination)
        shutil.move(str(p), str(dest))
        return dest

    @staticmethod
    def size(path: str | PathLib) -> int:
        return PathLib(path).stat().st_size

    @staticmethod
    def ensure_dir(path: str | PathLib) -> None:
        p = PathLib(path)
        if p.is_dir():
            return
        p.mkdir(parents=True, exist_ok=True)
