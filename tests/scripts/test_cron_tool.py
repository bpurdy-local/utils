"""Tests for cron_tool.py."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import cron_tool


class TestParseField:
    """Tests for parse_field function."""

    def test_asterisk(self):
        """Test asterisk (all values)."""
        result = cron_tool.parse_field("*", 0, 59, None)
        assert result == set(range(0, 60))

    def test_single_value(self):
        """Test single value."""
        result = cron_tool.parse_field("5", 0, 59, None)
        assert result == {5}

    def test_range(self):
        """Test range."""
        result = cron_tool.parse_field("1-5", 0, 59, None)
        assert result == {1, 2, 3, 4, 5}

    def test_step(self):
        """Test step value."""
        result = cron_tool.parse_field("*/15", 0, 59, None)
        assert result == {0, 15, 30, 45}

    def test_list(self):
        """Test list of values."""
        result = cron_tool.parse_field("1,3,5", 0, 59, None)
        assert result == {1, 3, 5}

    def test_combined(self):
        """Test combined expressions."""
        result = cron_tool.parse_field("1-3,10,20-22", 0, 59, None)
        assert result == {1, 2, 3, 10, 20, 21, 22}


class TestParseCron:
    """Tests for parse_cron function."""

    def test_every_minute(self):
        """Test every minute expression."""
        result = cron_tool.parse_cron("* * * * *")
        assert len(result) == 5
        assert result[0] == set(range(0, 60))  # minutes
        assert result[1] == set(range(0, 24))  # hours

    def test_specific_time(self):
        """Test specific time."""
        result = cron_tool.parse_cron("30 9 * * *")
        assert result[0] == {30}  # minute 30
        assert result[1] == {9}   # hour 9

    def test_weekdays(self):
        """Test weekday expression."""
        result = cron_tool.parse_cron("0 9 * * 1-5")
        assert result[4] == {1, 2, 3, 4, 5}  # Mon-Fri

    def test_special_daily(self):
        """Test @daily special expression."""
        result = cron_tool.parse_cron("@daily")
        assert result[0] == {0}   # minute 0
        assert result[1] == {0}   # hour 0

    def test_special_hourly(self):
        """Test @hourly special expression."""
        result = cron_tool.parse_cron("@hourly")
        assert result[0] == {0}   # minute 0
        assert result[1] == set(range(0, 24))  # all hours


class TestMatches:
    """Tests for matches function."""

    def test_matches(self):
        """Test datetime matching."""
        fields = cron_tool.parse_cron("30 9 * * *")
        dt = datetime(2024, 1, 15, 9, 30)
        assert cron_tool.matches(dt, fields)

    def test_not_matches(self):
        """Test datetime not matching."""
        fields = cron_tool.parse_cron("30 9 * * *")
        dt = datetime(2024, 1, 15, 9, 31)  # Wrong minute
        assert not cron_tool.matches(dt, fields)


class TestNextRun:
    """Tests for next_run function."""

    def test_next_run_single(self):
        """Test finding next run time."""
        fields = cron_tool.parse_cron("0 * * * *")  # Every hour
        start = datetime(2024, 1, 15, 9, 30)
        runs = cron_tool.next_run(fields, start, count=1)
        assert len(runs) == 1
        assert runs[0].minute == 0
        assert runs[0].hour == 10

    def test_next_run_multiple(self):
        """Test finding multiple next run times."""
        fields = cron_tool.parse_cron("*/15 * * * *")  # Every 15 min
        start = datetime(2024, 1, 15, 9, 0)
        runs = cron_tool.next_run(fields, start, count=4)
        assert len(runs) == 4


class TestExplainField:
    """Tests for explain_field function."""

    def test_explain_asterisk(self):
        """Test explaining asterisk."""
        result = cron_tool.explain_field("*", "minute", 0, 59)
        assert "every minute" in result

    def test_explain_step(self):
        """Test explaining step."""
        result = cron_tool.explain_field("*/5", "minute", 0, 59)
        assert "every 5" in result


class TestCmdValidate:
    """Tests for cmd_validate function."""

    def test_valid_expression(self, capsys):
        """Test validating valid expression."""
        args = argparse.Namespace(expression="0 9 * * 1-5")
        result = cron_tool.cmd_validate(args)
        assert result == 0

    def test_invalid_expression(self, capsys):
        """Test validating invalid expression."""
        args = argparse.Namespace(expression="invalid")
        result = cron_tool.cmd_validate(args)
        assert result == 1


class TestCmdNext:
    """Tests for cmd_next function."""

    def test_next_times(self, capsys):
        """Test getting next run times."""
        args = argparse.Namespace(
            expression="0 0 * * *",
            count=3,
            format="default",
        )
        result = cron_tool.cmd_next(args)
        assert result == 0
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert len(lines) == 3
