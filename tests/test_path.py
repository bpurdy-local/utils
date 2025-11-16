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


class TestPathProperties:
    """Test path property methods."""

    def test_extension(self):
        """Test extension method."""
        assert Path.extension("file.txt") == ".txt"
        assert Path.extension("archive.tar.gz") == ".gz"
        assert Path.extension("no_extension") == ""

    def test_get_stem(self):
        """Test get_stem method."""
        assert Path.get_stem("file.txt") == "file"
        assert Path.get_stem("archive.tar.gz") == "archive.tar"
        assert Path.get_stem("/path/to/file.txt") == "file"


class TestPathExists:
    """Test exists method."""

    def test_exists_file(self):
        """Test exists with existing file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            assert Path.exists(temp_path) is True
        finally:
            StdPath(temp_path).unlink()

    def test_exists_directory(self):
        """Test exists with existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            assert Path.exists(temp_dir) is True

    def test_exists_nonexistent(self):
        """Test exists with non-existent path."""
        assert Path.exists("/nonexistent/path/to/file.txt") is False

    def test_exists_with_path_object(self):
        """Test exists with Path object."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = StdPath(f.name)

        try:
            assert Path.exists(temp_path) is True
        finally:
            temp_path.unlink()

    def test_exists_relative_path(self):
        """Test exists with relative path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            import os

            original_dir = os.getcwd()
            try:
                os.chdir(temp_dir)
                # Create a file in the temp directory
                StdPath("test.txt").write_text("test")
                assert Path.exists("test.txt") is True
                assert Path.exists("nonexistent.txt") is False
            finally:
                os.chdir(original_dir)
