"""Tests for text_tool.py."""

import argparse
import sys
from io import StringIO
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import text_tool


class TestReadInput:
    """Tests for read_input function."""

    def test_read_from_file(self, temp_file):
        """Test reading from file."""
        path = temp_file("hello world")
        result = text_tool.read_input(str(path))
        assert result == "hello world"

    def test_read_from_stdin(self, monkeypatch):
        """Test reading from stdin."""
        monkeypatch.setattr(sys, "stdin", StringIO("stdin content"))
        result = text_tool.read_input(None)
        assert result == "stdin content"


class TestCmdReplace:
    """Tests for cmd_replace function."""

    def test_simple_replace(self, temp_file, capsys):
        """Test simple text replacement."""
        path = temp_file("hello world")
        args = argparse.Namespace(
            file=str(path),
            find="world",
            replace="universe",
            regex=False,
            ignore_case=False,
            output=None,
        )
        result = text_tool.cmd_replace(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "hello universe" in captured.out

    def test_regex_replace(self, temp_file, capsys):
        """Test regex replacement."""
        path = temp_file("order 12345")
        args = argparse.Namespace(
            file=str(path),
            find=r"\d+",
            replace="NUM",
            regex=True,
            ignore_case=False,
            output=None,
        )
        result = text_tool.cmd_replace(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "order NUM" in captured.out

    def test_case_insensitive_replace(self, temp_file, capsys):
        """Test case insensitive replacement."""
        path = temp_file("Hello HELLO hello")
        args = argparse.Namespace(
            file=str(path),
            find="hello",
            replace="hi",
            regex=False,
            ignore_case=True,
            output=None,
        )
        result = text_tool.cmd_replace(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "hi hi hi" in captured.out


class TestCmdExtract:
    """Tests for cmd_extract function."""

    def test_extract_emails(self, temp_file, capsys):
        """Test extracting email patterns."""
        path = temp_file("contact: user@example.com or admin@test.org")
        args = argparse.Namespace(
            file=str(path),
            pattern=r"[\w.]+@[\w.]+",
            ignore_case=False,
            unique=False,
        )
        result = text_tool.cmd_extract(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "user@example.com" in captured.out
        assert "admin@test.org" in captured.out

    def test_extract_unique(self, temp_file, capsys):
        """Test extracting unique matches."""
        path = temp_file("foo bar foo baz foo")
        args = argparse.Namespace(
            file=str(path),
            pattern=r"\w+",
            ignore_case=False,
            unique=True,
        )
        result = text_tool.cmd_extract(args)
        assert result == 0
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert len(lines) == 3  # foo, bar, baz (unique)


class TestCmdLines:
    """Tests for cmd_lines function."""

    def test_filter_contains(self, temp_file, capsys):
        """Test filtering lines containing text."""
        path = temp_file("line one\nerror here\nline two\nanother error")
        args = argparse.Namespace(
            file=str(path),
            contains="error",
            regex=None,
            startswith=None,
            endswith=None,
            invert=False,
            ignore_case=False,
            number=False,
            output=None,
        )
        result = text_tool.cmd_lines(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "error here" in captured.out
        assert "another error" in captured.out
        assert "line one" not in captured.out

    def test_filter_invert(self, temp_file, capsys):
        """Test inverting line filter."""
        path = temp_file("keep this\nremove this\nkeep that")
        args = argparse.Namespace(
            file=str(path),
            contains="remove",
            regex=None,
            startswith=None,
            endswith=None,
            invert=True,
            ignore_case=False,
            number=False,
            output=None,
        )
        result = text_tool.cmd_lines(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "keep this" in captured.out
        assert "keep that" in captured.out
        assert "remove this" not in captured.out


class TestCmdCase:
    """Tests for cmd_case function."""

    def test_upper(self, temp_file, capsys):
        """Test uppercase transformation."""
        path = temp_file("hello world")
        args = argparse.Namespace(
            file=str(path),
            transform="upper",
            output=None,
        )
        result = text_tool.cmd_case(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "HELLO WORLD" in captured.out

    def test_lower(self, temp_file, capsys):
        """Test lowercase transformation."""
        path = temp_file("HELLO WORLD")
        args = argparse.Namespace(
            file=str(path),
            transform="lower",
            output=None,
        )
        result = text_tool.cmd_case(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "hello world" in captured.out

    def test_title(self, temp_file, capsys):
        """Test title case transformation."""
        path = temp_file("hello world")
        args = argparse.Namespace(
            file=str(path),
            transform="title",
            output=None,
        )
        result = text_tool.cmd_case(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Hello World" in captured.out


class TestCmdCount:
    """Tests for cmd_count function."""

    def test_count_basic(self, temp_file, capsys):
        """Test basic counting."""
        path = temp_file("one two three\nfour five")
        args = argparse.Namespace(
            file=str(path),
            pattern=None,
            ignore_case=False,
        )
        result = text_tool.cmd_count(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Lines: 2" in captured.out
        assert "Words: 5" in captured.out

    def test_count_pattern(self, temp_file, capsys):
        """Test counting pattern matches."""
        path = temp_file("TODO: fix this\nTODO: add that\nDONE")
        args = argparse.Namespace(
            file=str(path),
            pattern="TODO",
            ignore_case=False,
        )
        result = text_tool.cmd_count(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Pattern matches: 2" in captured.out


class TestCmdSplit:
    """Tests for cmd_split function."""

    def test_split_delimiter(self, temp_file, capsys):
        """Test splitting by delimiter."""
        path = temp_file("a,b,c")
        args = argparse.Namespace(
            file=str(path),
            delimiter=",",
            regex=False,
        )
        result = text_tool.cmd_split(args)
        assert result == 0
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert lines == ["a", "b", "c"]


class TestCmdJoin:
    """Tests for cmd_join function."""

    def test_join_lines(self, temp_file, capsys):
        """Test joining lines."""
        path = temp_file("a\nb\nc")
        args = argparse.Namespace(
            file=str(path),
            delimiter=", ",
            output=None,
        )
        result = text_tool.cmd_join(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "a, b, c" in captured.out


class TestCmdReverse:
    """Tests for cmd_reverse function."""

    def test_reverse_text(self, temp_file, capsys):
        """Test reversing text."""
        path = temp_file("hello")
        args = argparse.Namespace(
            file=str(path),
            lines=False,
            output=None,
        )
        result = text_tool.cmd_reverse(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "olleh" in captured.out

    def test_reverse_lines(self, temp_file, capsys):
        """Test reversing line order."""
        path = temp_file("first\nsecond\nthird")
        args = argparse.Namespace(
            file=str(path),
            lines=True,
            output=None,
        )
        result = text_tool.cmd_reverse(args)
        assert result == 0
        captured = capsys.readouterr()
        assert captured.out.strip() == "third\nsecond\nfirst"
