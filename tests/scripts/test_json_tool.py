"""Tests for json_tool.py."""

import argparse
import json
import sys
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import json_tool


class TestCmdPretty:
    """Tests for cmd_pretty function."""

    def test_pretty_print(self, temp_file, capsys):
        """Test pretty printing JSON."""
        path = temp_file('{"a":1,"b":2}', name="test.json")
        args = argparse.Namespace(
            file=str(path),
            indent=2,
            output=None,
        )
        result = json_tool.cmd_pretty(args)
        assert result == 0
        captured = capsys.readouterr()
        assert '"a": 1' in captured.out
        assert '"b": 2' in captured.out

    def test_pretty_custom_indent(self, temp_file, capsys):
        """Test pretty printing with custom indent."""
        path = temp_file('{"a":1}', name="test.json")
        args = argparse.Namespace(
            file=str(path),
            indent=4,
            output=None,
        )
        result = json_tool.cmd_pretty(args)
        assert result == 0
        captured = capsys.readouterr()
        # 4-space indent should produce more spaces
        assert '    "a"' in captured.out


class TestCmdMinify:
    """Tests for cmd_minify function."""

    def test_minify(self, temp_file, capsys):
        """Test minifying JSON."""
        content = '{\n  "a": 1,\n  "b": 2\n}'
        path = temp_file(content, name="test.json")
        args = argparse.Namespace(
            file=str(path),
            output=None,
        )
        result = json_tool.cmd_minify(args)
        assert result == 0
        captured = capsys.readouterr()
        assert captured.out.strip() == '{"a":1,"b":2}'


class TestCmdQuery:
    """Tests for cmd_query function."""

    def test_query_simple(self, temp_file, capsys):
        """Test simple query."""
        path = temp_file('{"user": {"name": "John", "age": 30}}', name="test.json")
        args = argparse.Namespace(
            file=str(path),
            path="user.name",
            output=None,
        )
        result = json_tool.cmd_query(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "John" in captured.out

    def test_query_array(self, temp_file, capsys):
        """Test array query."""
        path = temp_file('{"items": [1, 2, 3]}', name="test.json")
        args = argparse.Namespace(
            file=str(path),
            path="items.1",
            output=None,
        )
        result = json_tool.cmd_query(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "2" in captured.out


class TestCmdFlatten:
    """Tests for cmd_flatten function."""

    def test_flatten(self, temp_file, capsys):
        """Test flattening nested JSON."""
        path = temp_file('{"a": {"b": {"c": 1}}}', name="test.json")
        args = argparse.Namespace(
            file=str(path),
            sep=".",
            output=None,
        )
        result = json_tool.cmd_flatten(args)
        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "a.b.c" in output
        assert output["a.b.c"] == 1


class TestCmdUnflatten:
    """Tests for cmd_unflatten function."""

    def test_unflatten(self, temp_file, capsys):
        """Test unflattening JSON."""
        path = temp_file('{"a.b.c": 1}', name="test.json")
        args = argparse.Namespace(
            file=str(path),
            sep=".",
            output=None,
        )
        result = json_tool.cmd_unflatten(args)
        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["a"]["b"]["c"] == 1


class TestCmdValidate:
    """Tests for cmd_validate function."""

    def test_validate_valid(self, temp_file, capsys):
        """Test validating valid JSON."""
        path = temp_file('{"valid": true}', name="test.json")
        args = argparse.Namespace(
            file=str(path),
        )
        result = json_tool.cmd_validate(args)
        assert result == 0

    def test_validate_invalid(self, temp_file, capsys):
        """Test validating invalid JSON."""
        path = temp_file('{invalid json}', name="test.json")
        args = argparse.Namespace(
            file=str(path),
        )
        result = json_tool.cmd_validate(args)
        assert result == 1


class TestCmdKeys:
    """Tests for cmd_keys function."""

    def test_keys(self, temp_file, capsys):
        """Test listing keys."""
        path = temp_file('{"a": 1, "b": 2, "c": 3}', name="test.json")
        args = argparse.Namespace(
            file=str(path),
            output=None,
        )
        result = json_tool.cmd_keys(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "a" in captured.out
        assert "b" in captured.out
        assert "c" in captured.out
