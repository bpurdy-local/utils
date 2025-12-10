"""Tests for env_tool.py."""

import argparse
import sys
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import env_tool


class TestParseEnvFile:
    """Tests for parse_env_file function."""

    def test_parse_simple(self, temp_file):
        """Test parsing simple env file."""
        path = temp_file("KEY=value\nANOTHER=test", name=".env")
        result = env_tool.parse_env_file(str(path))
        assert result == {"KEY": "value", "ANOTHER": "test"}

    def test_parse_with_quotes(self, temp_file):
        """Test parsing with quoted values."""
        path = temp_file('KEY="quoted value"\nOTHER=\'single\'', name=".env")
        result = env_tool.parse_env_file(str(path))
        assert result == {"KEY": "quoted value", "OTHER": "single"}

    def test_parse_with_comments(self, temp_file):
        """Test parsing with comments."""
        path = temp_file("# comment\nKEY=value\n# another comment", name=".env")
        result = env_tool.parse_env_file(str(path))
        assert result == {"KEY": "value"}

    def test_parse_empty_file(self, temp_dir):
        """Test parsing nonexistent file."""
        result = env_tool.parse_env_file(str(temp_dir / "nonexistent"))
        assert result == {}


class TestCmdGet:
    """Tests for cmd_get function."""

    def test_get_existing(self, temp_file, capsys):
        """Test getting existing variable."""
        path = temp_file("MY_VAR=hello", name=".env")
        args = argparse.Namespace(
            file=str(path),
            key="MY_VAR",
            default=None,
        )
        result = env_tool.cmd_get(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "hello" in captured.out

    def test_get_missing_with_default(self, temp_file, capsys):
        """Test getting missing variable with default."""
        path = temp_file("OTHER=value", name=".env")
        args = argparse.Namespace(
            file=str(path),
            key="MISSING",
            default="fallback",
        )
        result = env_tool.cmd_get(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "fallback" in captured.out


class TestCmdSet:
    """Tests for cmd_set function."""

    def test_set_new(self, temp_file, capsys):
        """Test setting new variable."""
        path = temp_file("EXISTING=value", name=".env")
        args = argparse.Namespace(
            file=str(path),
            key="NEW_KEY",
            value="new_value",
        )
        result = env_tool.cmd_set(args)
        assert result == 0

        # Verify it was written
        parsed = env_tool.parse_env_file(str(path))
        assert parsed["NEW_KEY"] == "new_value"


class TestCmdList:
    """Tests for cmd_list function."""

    def test_list_keys(self, temp_file, capsys):
        """Test listing keys."""
        path = temp_file("KEY1=value1\nKEY2=value2", name=".env")
        args = argparse.Namespace(
            file=str(path),
            values=False,
            mask=False,
        )
        result = env_tool.cmd_list(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "KEY1" in captured.out
        assert "KEY2" in captured.out

    def test_list_with_values(self, temp_file, capsys):
        """Test listing with values."""
        path = temp_file("KEY=value", name=".env")
        args = argparse.Namespace(
            file=str(path),
            values=True,
            mask=False,
        )
        result = env_tool.cmd_list(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "KEY" in captured.out
        assert "value" in captured.out


class TestCmdDiff:
    """Tests for cmd_diff function."""

    def test_diff_identical(self, temp_dir, capsys):
        """Test diffing identical files."""
        file1 = temp_dir / ".env1"
        file2 = temp_dir / ".env2"
        file1.write_text("KEY=value")
        file2.write_text("KEY=value")

        args = argparse.Namespace(
            file1=str(file1),
            file2=str(file2),
        )
        result = env_tool.cmd_diff(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "identical" in captured.out.lower()

    def test_diff_different(self, temp_dir, capsys):
        """Test diffing different files."""
        file1 = temp_dir / ".env1"
        file2 = temp_dir / ".env2"
        file1.write_text("KEY1=value1")
        file2.write_text("KEY2=value2")

        args = argparse.Namespace(
            file1=str(file1),
            file2=str(file2),
        )
        result = env_tool.cmd_diff(args)
        assert result == 1
        captured = capsys.readouterr()
        assert "KEY1" in captured.out
        assert "KEY2" in captured.out


class TestCmdValidate:
    """Tests for cmd_validate function."""

    def test_validate_all_present(self, temp_file, capsys):
        """Test validation when all required vars present."""
        path = temp_file("DB_HOST=localhost\nDB_PORT=5432", name=".env")
        args = argparse.Namespace(
            file=str(path),
            required=["DB_HOST", "DB_PORT"],
        )
        result = env_tool.cmd_validate(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "All required" in captured.out

    def test_validate_missing(self, temp_file, capsys):
        """Test validation when vars missing."""
        path = temp_file("DB_HOST=localhost", name=".env")
        args = argparse.Namespace(
            file=str(path),
            required=["DB_HOST", "DB_PORT", "DB_USER"],
        )
        result = env_tool.cmd_validate(args)
        assert result == 1
        captured = capsys.readouterr()
        assert "Missing" in captured.out
        assert "DB_PORT" in captured.out
