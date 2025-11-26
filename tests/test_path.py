"""Comprehensive tests for Path wrapper class."""

import tempfile
from pathlib import Path as StdPath

from utils import Path


class TestPathFileOperations:
    """Test file read/write operations."""

    def test_read_write(self):
        """Test read and write operations."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_path = f.name

        try:
            Path.write(temp_path, content="Hello World")
            assert Path.read(temp_path) == "Hello World"
        finally:
            StdPath(temp_path).unlink()

    def test_read_lines_write_lines(self):
        """Test read_lines and write_lines."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_path = f.name

        try:
            Path.write_lines(temp_path, lines=["line1", "line2", "line3"])
            lines = Path.read_lines(temp_path)
            assert lines == ["line1", "line2", "line3"]
        finally:
            StdPath(temp_path).unlink()

    def test_read_json_write_json(self):
        """Test read_json and write_json."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_path = f.name

        try:
            data = {"key": "value", "number": 123}
            Path.write_json(temp_path, data=data)
            result = Path.read_json(temp_path)
            assert result == data
        finally:
            StdPath(temp_path).unlink()


