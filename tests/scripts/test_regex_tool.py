"""Tests for regex_tool.py."""

import argparse
import sys
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import regex_tool


class TestHighlightMatches:
    """Tests for highlight_matches function."""

    def test_no_matches(self):
        """Test with no matches."""
        result = regex_tool.highlight_matches("hello", [])
        assert result == "hello"


class TestCmdTest:
    """Tests for cmd_test function."""

    def test_simple_match(self, capsys):
        """Test simple pattern matching."""
        args = argparse.Namespace(
            pattern=r"\d+",
            text="Order 12345",
            file=None,
            ignore_case=False,
            multiline=False,
            dotall=False,
            show_groups=False,
        )
        result = regex_tool.cmd_test(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Matches: 1" in captured.out

    def test_no_match(self, capsys):
        """Test no match."""
        args = argparse.Namespace(
            pattern=r"\d+",
            text="no numbers here",
            file=None,
            ignore_case=False,
            multiline=False,
            dotall=False,
            show_groups=False,
        )
        result = regex_tool.cmd_test(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Matches: 0" in captured.out
        assert "No matches" in captured.out

    def test_case_insensitive(self, capsys):
        """Test case insensitive matching."""
        args = argparse.Namespace(
            pattern=r"hello",
            text="HELLO world",
            file=None,
            ignore_case=True,
            multiline=False,
            dotall=False,
            show_groups=False,
        )
        result = regex_tool.cmd_test(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Matches: 1" in captured.out

    def test_with_groups(self, capsys):
        """Test showing capture groups."""
        args = argparse.Namespace(
            pattern=r"(\w+)@(\w+\.\w+)",
            text="test@example.com",
            file=None,
            ignore_case=False,
            multiline=False,
            dotall=False,
            show_groups=True,
        )
        result = regex_tool.cmd_test(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Group 1:" in captured.out
        assert "Group 2:" in captured.out

    def test_invalid_regex(self, capsys):
        """Test invalid regex pattern."""
        args = argparse.Namespace(
            pattern=r"[invalid",
            text="test",
            file=None,
            ignore_case=False,
            multiline=False,
            dotall=False,
            show_groups=False,
        )
        result = regex_tool.cmd_test(args)
        assert result == 1


class TestCmdReplace:
    """Tests for cmd_replace function."""

    def test_simple_replace(self, capsys):
        """Test simple replacement."""
        args = argparse.Namespace(
            pattern=r"\d+",
            replacement="XXX",
            text="Order 12345",
            file=None,
            output=None,
            ignore_case=False,
            multiline=False,
        )
        result = regex_tool.cmd_replace(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Order XXX" in captured.out

    def test_backreference_replace(self, capsys):
        """Test replacement with backreferences."""
        args = argparse.Namespace(
            pattern=r"(\w+), (\w+)",
            replacement=r"\2 \1",
            text="Doe, John",
            file=None,
            output=None,
            ignore_case=False,
            multiline=False,
        )
        result = regex_tool.cmd_replace(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "John Doe" in captured.out


class TestCmdSplit:
    """Tests for cmd_split function."""

    def test_split(self, capsys):
        """Test splitting by pattern."""
        args = argparse.Namespace(
            pattern=r"[,;\s]+",
            text="a, b; c d",
            file=None,
            max=None,
        )
        result = regex_tool.cmd_split(args)
        assert result == 0
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert "a" in lines
        assert "b" in lines
        assert "c" in lines
        assert "d" in lines


class TestCmdExtract:
    """Tests for cmd_extract function."""

    def test_extract(self, capsys):
        """Test extracting matches."""
        args = argparse.Namespace(
            pattern=r"\d+",
            text="a1 b2 c3",
            file=None,
            ignore_case=False,
            unique=False,
        )
        result = regex_tool.cmd_extract(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "1" in captured.out
        assert "2" in captured.out
        assert "3" in captured.out

    def test_extract_unique(self, capsys):
        """Test extracting unique matches."""
        args = argparse.Namespace(
            pattern=r"\d+",
            text="a1 b1 c2",
            file=None,
            ignore_case=False,
            unique=True,
        )
        result = regex_tool.cmd_extract(args)
        assert result == 0
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert len(lines) == 2  # "1" and "2" (unique)


class TestCmdExplain:
    """Tests for cmd_explain function."""

    def test_explain(self, capsys):
        """Test explaining regex pattern."""
        args = argparse.Namespace(pattern=r"^\d+$")
        result = regex_tool.cmd_explain(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Start of string" in captured.out
        assert "End of string" in captured.out
        assert "Digit" in captured.out
