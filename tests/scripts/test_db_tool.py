"""Tests for db_tool.py."""

import argparse
import sqlite3
import sys
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import db_tool


class TestFormatValue:
    """Tests for format_value function."""

    def test_none_value(self):
        """Test formatting None."""
        result = db_tool.format_value(None)
        assert "NULL" in result

    def test_bytes_value(self):
        """Test formatting bytes."""
        result = db_tool.format_value(b"test")
        assert "bytes" in result

    def test_string_value(self):
        """Test formatting string."""
        result = db_tool.format_value("hello")
        assert result == "hello"


class TestCmdQuery:
    """Tests for cmd_query function."""

    def test_select_query(self, temp_dir, capsys):
        """Test SELECT query."""
        db_path = temp_dir / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
        conn.execute("INSERT INTO users VALUES (1, 'Alice')")
        conn.execute("INSERT INTO users VALUES (2, 'Bob')")
        conn.commit()
        conn.close()

        args = argparse.Namespace(
            database=str(db_path),
            sql="SELECT * FROM users",
            format="table",
        )
        result = db_tool.cmd_query(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Alice" in captured.out
        assert "Bob" in captured.out

    def test_query_json_format(self, temp_dir, capsys):
        """Test query with JSON output."""
        db_path = temp_dir / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
        conn.execute("INSERT INTO users VALUES (1, 'Alice')")
        conn.commit()
        conn.close()

        args = argparse.Namespace(
            database=str(db_path),
            sql="SELECT * FROM users",
            format="json",
        )
        result = db_tool.cmd_query(args)
        assert result == 0
        captured = capsys.readouterr()
        assert '"name": "Alice"' in captured.out


class TestCmdTables:
    """Tests for cmd_tables function."""

    def test_list_tables(self, temp_dir, capsys):
        """Test listing tables."""
        db_path = temp_dir / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE users (id INTEGER)")
        conn.execute("CREATE TABLE orders (id INTEGER)")
        conn.commit()
        conn.close()

        args = argparse.Namespace(database=str(db_path))
        result = db_tool.cmd_tables(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "users" in captured.out
        assert "orders" in captured.out


class TestCmdSchema:
    """Tests for cmd_schema function."""

    def test_show_schema(self, temp_dir, capsys):
        """Test showing schema."""
        db_path = temp_dir / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        conn.commit()
        conn.close()

        args = argparse.Namespace(
            database=str(db_path),
            table="users",
        )
        result = db_tool.cmd_schema(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "CREATE TABLE" in captured.out
        assert "users" in captured.out


class TestCmdDescribe:
    """Tests for cmd_describe function."""

    def test_describe_table(self, temp_dir, capsys):
        """Test describing table."""
        db_path = temp_dir / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
        conn.commit()
        conn.close()

        args = argparse.Namespace(
            database=str(db_path),
            table="users",
        )
        result = db_tool.cmd_describe(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "id" in captured.out
        assert "name" in captured.out
        assert "INTEGER" in captured.out


class TestCmdDump:
    """Tests for cmd_dump function."""

    def test_dump_table(self, temp_dir, capsys):
        """Test dumping table."""
        db_path = temp_dir / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
        conn.execute("INSERT INTO users VALUES (1, 'Alice')")
        conn.commit()
        conn.close()

        args = argparse.Namespace(
            database=str(db_path),
            table="users",
            format="sql",
        )
        result = db_tool.cmd_dump(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "INSERT INTO" in captured.out
        assert "Alice" in captured.out


class TestCmdImportCsv:
    """Tests for cmd_import_csv function."""

    def test_import_csv(self, temp_dir, capsys):
        """Test importing CSV."""
        db_path = temp_dir / "test.db"
        csv_path = temp_dir / "data.csv"
        csv_path.write_text("name,age\nAlice,30\nBob,25")

        args = argparse.Namespace(
            database=str(db_path),
            csv_file=str(csv_path),
            table=None,
            create=True,
        )
        result = db_tool.cmd_import_csv(args)
        assert result == 0

        # Verify data was imported
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM data")
        rows = cursor.fetchall()
        conn.close()
        assert len(rows) == 2


class TestCmdVacuum:
    """Tests for cmd_vacuum function."""

    def test_vacuum(self, temp_dir, capsys):
        """Test vacuum command."""
        db_path = temp_dir / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE users (id INTEGER)")
        for i in range(100):
            conn.execute("INSERT INTO users VALUES (?)", (i,))
        conn.execute("DELETE FROM users")
        conn.commit()
        conn.close()

        args = argparse.Namespace(database=str(db_path))
        result = db_tool.cmd_vacuum(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Before:" in captured.out
        assert "After:" in captured.out
