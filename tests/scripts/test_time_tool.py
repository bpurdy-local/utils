"""Tests for time_tool.py."""

import argparse
import sys
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import time_tool


class TestCmdNow:
    """Tests for cmd_now function."""

    def test_now_default(self, capsys):
        """Test showing current time."""
        args = argparse.Namespace(timezone=None, format=None)
        result = time_tool.cmd_now(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Local:" in captured.out
        assert "UTC:" in captured.out
        assert "Unix:" in captured.out

    def test_now_custom_format(self, capsys):
        """Test custom time format."""
        args = argparse.Namespace(timezone=None, format="%Y-%m-%d")
        result = time_tool.cmd_now(args)
        assert result == 0
        captured = capsys.readouterr()
        # Should match YYYY-MM-DD pattern
        assert len(captured.out.strip()) == 10
        assert "-" in captured.out

    def test_now_invalid_timezone(self, capsys):
        """Test invalid timezone."""
        args = argparse.Namespace(timezone="Invalid/Zone", format=None)
        result = time_tool.cmd_now(args)
        assert result == 1


class TestCmdConvert:
    """Tests for cmd_convert function."""

    def test_convert_unix(self, capsys):
        """Test converting Unix timestamp."""
        args = argparse.Namespace(
            input="1705315845",
            to_tz=None,
            format=None,
            unix=False,
            iso=True,
        )
        result = time_tool.cmd_convert(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "2024-01-15" in captured.out

    def test_convert_to_unix(self, capsys):
        """Test converting to Unix timestamp."""
        args = argparse.Namespace(
            input="2024-01-15T10:30:45",
            to_tz=None,
            format=None,
            unix=True,
            iso=False,
        )
        result = time_tool.cmd_convert(args)
        assert result == 0
        captured = capsys.readouterr()
        # Should be a number
        assert captured.out.strip().isdigit()


class TestCmdDiff:
    """Tests for cmd_diff function."""

    def test_diff_dates(self, capsys):
        """Test calculating date difference."""
        args = argparse.Namespace(
            time1="2024-01-01",
            time2="2024-01-31",
        )
        result = time_tool.cmd_diff(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Days:" in captured.out
        assert "30" in captured.out


class TestCmdAdd:
    """Tests for cmd_add function."""

    def test_add_days(self, capsys):
        """Test adding days."""
        args = argparse.Namespace(
            time="2024-01-15",
            days=10,
            hours=0,
            minutes=0,
            seconds=0,
            weeks=0,
            format="%Y-%m-%d",
        )
        result = time_tool.cmd_add(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "2024-01-25" in captured.out


class TestCmdZones:
    """Tests for cmd_zones function."""

    def test_list_zones(self, capsys):
        """Test listing timezones."""
        args = argparse.Namespace(search=None, with_offset=False)
        result = time_tool.cmd_zones(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "America" in captured.out or "Europe" in captured.out

    def test_search_zones(self, capsys):
        """Test searching timezones."""
        args = argparse.Namespace(search="tokyo", with_offset=False)
        result = time_tool.cmd_zones(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Tokyo" in captured.out


class TestCmdEpoch:
    """Tests for cmd_epoch function."""

    def test_epoch_current(self, capsys):
        """Test showing current epoch."""
        args = argparse.Namespace(value=None)
        result = time_tool.cmd_epoch(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "seconds" in captured.out
        assert "milliseconds" in captured.out

    def test_epoch_convert(self, capsys):
        """Test converting epoch."""
        args = argparse.Namespace(value="1705315845")
        result = time_tool.cmd_epoch(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "2024-01-15" in captured.out
