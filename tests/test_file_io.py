"""Comprehensive tests for FileIO class."""

import tempfile
from pathlib import Path as StdPath

from utils import FileIO


class TestFileIOReadWrite:
    """Test FileIO read and write methods."""

    def test_read_write(self):
        """Test FileIO.read and FileIO.write."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_path = f.name

        try:
            FileIO.write(temp_path, content="Hello World")
            content = FileIO.read(temp_path)
            assert content == "Hello World"
        finally:
            StdPath(temp_path).unlink()

    def test_read_lines_write_lines(self):
        """Test FileIO.read_lines and FileIO.write_lines."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_path = f.name

        try:
            FileIO.write_lines(temp_path, lines=["line1", "line2", "line3"])
            lines = FileIO.read_lines(temp_path)
            assert lines == ["line1", "line2", "line3"]
        finally:
            StdPath(temp_path).unlink()

    def test_read_json_write_json(self):
        """Test FileIO.read_json and FileIO.write_json."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_path = f.name

        try:
            data = {"key": "value", "number": 123}
            FileIO.write_json(temp_path, data=data)
            result = FileIO.read_json(temp_path)
            assert result == data
        finally:
            StdPath(temp_path).unlink()


class TestFileIOEnsureDir:
    """Test FileIO.ensure_dir method."""

    def test_ensure_dir(self):
        """Test FileIO.ensure_dir creates directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dirpath = StdPath(tmpdir) / "new" / "nested" / "dir"
            FileIO.ensure_dir(dirpath)
            assert dirpath.exists()
            assert dirpath.is_dir()


class TestFileIOCopyMove:
    """Test FileIO copy and move methods."""

    def test_copy(self):
        """Test FileIO.copy."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = StdPath(tmpdir) / "source.txt"
            destination = StdPath(tmpdir) / "dest.txt"

            source.write_text("test content")
            result = FileIO.copy(source, destination=destination)

            assert destination.exists()
            assert destination.read_text() == "test content"
            assert isinstance(result, StdPath)

    def test_move(self):
        """Test FileIO.move."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = StdPath(tmpdir) / "source.txt"
            destination = StdPath(tmpdir) / "dest.txt"

            source.write_text("test content")
            result = FileIO.move(source, destination=destination)

            assert not source.exists()
            assert destination.exists()
            assert destination.read_text() == "test content"
            assert isinstance(result, StdPath)
