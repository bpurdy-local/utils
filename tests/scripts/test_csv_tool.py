"""Tests for csv_tool.py."""

import argparse
import json
import sys
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import csv_tool


class TestReadCsv:
    """Tests for read_csv function."""

    def test_read_csv_from_file(self, temp_file):
        """Test reading CSV from file."""
        path = temp_file("name,age\nAlice,30\nBob,25", name="test.csv")
        headers, rows = csv_tool.read_csv(str(path), delimiter=",")
        assert headers == ["name", "age"]
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"
        assert rows[1]["age"] == "25"


class TestCmdHead:
    """Tests for cmd_head function."""

    def test_head_default(self, temp_file, capsys):
        """Test head with default count."""
        content = "name,age\n" + "\n".join(f"Person{i},{i}" for i in range(20))
        path = temp_file(content, name="test.csv")
        args = argparse.Namespace(
            file=str(path),
            n=10,
            delimiter=",",
            output=None,
        )
        result = csv_tool.cmd_head(args)
        assert result == 0
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert len(lines) == 11  # header + 10 rows

    def test_head_custom_count(self, temp_file, capsys):
        """Test head with custom count."""
        content = "name,age\n" + "\n".join(f"Person{i},{i}" for i in range(20))
        path = temp_file(content, name="test.csv")
        args = argparse.Namespace(
            file=str(path),
            n=5,
            delimiter=",",
            output=None,
        )
        result = csv_tool.cmd_head(args)
        assert result == 0
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert len(lines) == 6  # header + 5 rows


class TestCmdTail:
    """Tests for cmd_tail function."""

    def test_tail(self, temp_file, capsys):
        """Test tail function."""
        content = "name,age\n" + "\n".join(f"Person{i},{i}" for i in range(20))
        path = temp_file(content, name="test.csv")
        args = argparse.Namespace(
            file=str(path),
            n=5,
            delimiter=",",
            output=None,
        )
        result = csv_tool.cmd_tail(args)
        assert result == 0
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert len(lines) == 6  # header + 5 rows
        assert "Person19" in captured.out


class TestCmdColumns:
    """Tests for cmd_columns function."""

    def test_columns(self, temp_file, capsys):
        """Test listing columns."""
        path = temp_file("name,age,email\nAlice,30,alice@test.com", name="test.csv")
        args = argparse.Namespace(
            file=str(path),
            delimiter=",",
        )
        result = csv_tool.cmd_columns(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "1. name" in captured.out
        assert "2. age" in captured.out
        assert "3. email" in captured.out


class TestCmdSelect:
    """Tests for cmd_select function."""

    def test_select_columns(self, temp_file, capsys):
        """Test selecting columns."""
        path = temp_file("name,age,email\nAlice,30,alice@test.com", name="test.csv")
        args = argparse.Namespace(
            file=str(path),
            cols="name,email",
            delimiter=",",
            output=None,
        )
        result = csv_tool.cmd_select(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "name,email" in captured.out
        assert "age" not in captured.out

    def test_select_invalid_column(self, temp_file, capsys):
        """Test selecting invalid column."""
        path = temp_file("name,age\nAlice,30", name="test.csv")
        args = argparse.Namespace(
            file=str(path),
            cols="name,invalid",
            delimiter=",",
            output=None,
        )
        result = csv_tool.cmd_select(args)
        assert result == 1


class TestCmdFilter:
    """Tests for cmd_filter function."""

    def test_filter_eq(self, temp_file, capsys):
        """Test filter with eq operator."""
        path = temp_file("name,status\nAlice,active\nBob,inactive", name="test.csv")
        args = argparse.Namespace(
            file=str(path),
            condition="status:eq:active",
            delimiter=",",
            output=None,
        )
        result = csv_tool.cmd_filter(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Alice" in captured.out
        assert "Bob" not in captured.out

    def test_filter_gt(self, temp_file, capsys):
        """Test filter with gt operator."""
        path = temp_file("name,age\nAlice,30\nBob,25\nCharlie,35", name="test.csv")
        args = argparse.Namespace(
            file=str(path),
            condition="age:gt:28",
            delimiter=",",
            output=None,
        )
        result = csv_tool.cmd_filter(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Alice" in captured.out
        assert "Charlie" in captured.out
        assert "Bob" not in captured.out

    def test_filter_contains(self, temp_file, capsys):
        """Test filter with contains operator."""
        path = temp_file("name,email\nAlice,alice@gmail.com\nBob,bob@yahoo.com", name="test.csv")
        args = argparse.Namespace(
            file=str(path),
            condition="email:contains:@gmail",
            delimiter=",",
            output=None,
        )
        result = csv_tool.cmd_filter(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Alice" in captured.out
        assert "Bob" not in captured.out


class TestCmdSort:
    """Tests for cmd_sort function."""

    def test_sort_alphabetic(self, temp_file, capsys):
        """Test alphabetic sort."""
        path = temp_file("name,age\nCharlie,30\nAlice,25\nBob,35", name="test.csv")
        args = argparse.Namespace(
            file=str(path),
            col="name",
            numeric=False,
            reverse=False,
            delimiter=",",
            output=None,
        )
        result = csv_tool.cmd_sort(args)
        assert result == 0
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert "Alice" in lines[1]

    def test_sort_numeric(self, temp_file, capsys):
        """Test numeric sort."""
        path = temp_file("name,age\nAlice,30\nBob,25\nCharlie,35", name="test.csv")
        args = argparse.Namespace(
            file=str(path),
            col="age",
            numeric=True,
            reverse=False,
            delimiter=",",
            output=None,
        )
        result = csv_tool.cmd_sort(args)
        assert result == 0
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert "Bob" in lines[1]  # Bob has lowest age


class TestCmdUnique:
    """Tests for cmd_unique function."""

    def test_unique(self, temp_file, capsys):
        """Test unique values."""
        path = temp_file("name,country\nAlice,USA\nBob,USA\nCharlie,Canada", name="test.csv")
        args = argparse.Namespace(
            file=str(path),
            col="country",
            count=False,
            delimiter=",",
        )
        result = csv_tool.cmd_unique(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "USA" in captured.out
        assert "Canada" in captured.out

    def test_unique_with_count(self, temp_file, capsys):
        """Test unique values with count."""
        path = temp_file("name,country\nAlice,USA\nBob,USA\nCharlie,Canada", name="test.csv")
        args = argparse.Namespace(
            file=str(path),
            col="country",
            count=True,
            delimiter=",",
        )
        result = csv_tool.cmd_unique(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "2\tUSA" in captured.out
        assert "1\tCanada" in captured.out


class TestCmdToJson:
    """Tests for cmd_to_json function."""

    def test_to_json(self, temp_file, capsys):
        """Test CSV to JSON conversion."""
        path = temp_file("name,age\nAlice,30\nBob,25", name="test.csv")
        args = argparse.Namespace(
            file=str(path),
            delimiter=",",
            output=None,
        )
        result = csv_tool.cmd_to_json(args)
        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data) == 2
        assert data[0]["name"] == "Alice"


class TestCmdFromJson:
    """Tests for cmd_from_json function."""

    def test_from_json(self, temp_file, capsys):
        """Test JSON to CSV conversion."""
        json_content = '[{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]'
        path = temp_file(json_content, name="test.json")
        args = argparse.Namespace(
            file=str(path),
            delimiter=",",
            output=None,
        )
        result = csv_tool.cmd_from_json(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "name,age" in captured.out or "age,name" in captured.out
        assert "Alice" in captured.out
        assert "Bob" in captured.out
