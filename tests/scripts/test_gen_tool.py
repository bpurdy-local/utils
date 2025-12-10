"""Tests for gen_tool.py."""

import argparse
import re
import sys
import uuid as uuid_module
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import gen_tool


class TestCmdUuid:
    """Tests for cmd_uuid function."""

    def test_generate_single(self, capsys):
        """Test generating single UUID."""
        args = argparse.Namespace(count=1, upper=False)
        result = gen_tool.cmd_uuid(args)
        assert result == 0
        captured = capsys.readouterr()
        # Validate UUID format
        uuid_str = captured.out.strip()
        uuid_module.UUID(uuid_str)  # Raises if invalid

    def test_generate_multiple(self, capsys):
        """Test generating multiple UUIDs."""
        args = argparse.Namespace(count=5, upper=False)
        result = gen_tool.cmd_uuid(args)
        assert result == 0
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert len(lines) == 5

    def test_generate_uppercase(self, capsys):
        """Test generating uppercase UUIDs."""
        args = argparse.Namespace(count=1, upper=True)
        result = gen_tool.cmd_uuid(args)
        assert result == 0
        captured = capsys.readouterr()
        assert captured.out.strip() == captured.out.strip().upper()


class TestCmdPassword:
    """Tests for cmd_password function."""

    def test_generate_password(self, capsys):
        """Test generating password."""
        args = argparse.Namespace(
            count=1,
            length=16,
            no_upper=False,
            no_lower=False,
            no_digits=False,
            no_special=False,
        )
        result = gen_tool.cmd_password(args)
        assert result == 0
        captured = capsys.readouterr()
        password = captured.out.strip()
        assert len(password) == 16

    def test_password_length(self, capsys):
        """Test password length."""
        args = argparse.Namespace(
            count=1,
            length=32,
            no_upper=False,
            no_lower=False,
            no_digits=False,
            no_special=False,
        )
        result = gen_tool.cmd_password(args)
        assert result == 0
        captured = capsys.readouterr()
        password = captured.out.strip()
        assert len(password) == 32

    def test_password_no_special(self, capsys):
        """Test password without special characters."""
        args = argparse.Namespace(
            count=1,
            length=20,
            no_upper=False,
            no_lower=False,
            no_digits=False,
            no_special=True,
        )
        result = gen_tool.cmd_password(args)
        assert result == 0
        captured = capsys.readouterr()
        password = captured.out.strip()
        assert password.isalnum()


class TestCmdString:
    """Tests for cmd_string function."""

    def test_generate_alphanumeric(self, capsys):
        """Test generating alphanumeric string."""
        args = argparse.Namespace(
            count=1,
            length=10,
            alpha=False,
            digits=False,
            hex=False,
            chars=None,
        )
        result = gen_tool.cmd_string(args)
        assert result == 0
        captured = capsys.readouterr()
        s = captured.out.strip()
        assert len(s) == 10
        assert s.isalnum()

    def test_generate_alpha_only(self, capsys):
        """Test generating letters only."""
        args = argparse.Namespace(
            count=1,
            length=10,
            alpha=True,
            digits=False,
            hex=False,
            chars=None,
        )
        result = gen_tool.cmd_string(args)
        assert result == 0
        captured = capsys.readouterr()
        s = captured.out.strip()
        assert s.isalpha()

    def test_generate_digits_only(self, capsys):
        """Test generating digits only."""
        args = argparse.Namespace(
            count=1,
            length=10,
            alpha=False,
            digits=True,
            hex=False,
            chars=None,
        )
        result = gen_tool.cmd_string(args)
        assert result == 0
        captured = capsys.readouterr()
        s = captured.out.strip()
        assert s.isdigit()

    def test_generate_custom_charset(self, capsys):
        """Test generating with custom charset."""
        args = argparse.Namespace(
            count=1,
            length=20,
            alpha=False,
            digits=False,
            hex=False,
            chars="ACGT",
        )
        result = gen_tool.cmd_string(args)
        assert result == 0
        captured = capsys.readouterr()
        s = captured.out.strip()
        assert all(c in "ACGT" for c in s)


class TestCmdHex:
    """Tests for cmd_hex function."""

    def test_generate_hex(self, capsys):
        """Test generating hex string."""
        args = argparse.Namespace(count=1, length=16, upper=False)
        result = gen_tool.cmd_hex(args)
        assert result == 0
        captured = capsys.readouterr()
        s = captured.out.strip()
        assert len(s) == 16
        assert all(c in "0123456789abcdef" for c in s)

    def test_generate_hex_upper(self, capsys):
        """Test generating uppercase hex."""
        args = argparse.Namespace(count=1, length=16, upper=True)
        result = gen_tool.cmd_hex(args)
        assert result == 0
        captured = capsys.readouterr()
        s = captured.out.strip()
        assert s == s.upper()


class TestCmdInt:
    """Tests for cmd_int function."""

    def test_generate_int(self, capsys):
        """Test generating random integer."""
        args = argparse.Namespace(count=1, min=0, max=100)
        result = gen_tool.cmd_int(args)
        assert result == 0
        captured = capsys.readouterr()
        n = int(captured.out.strip())
        assert 0 <= n <= 100

    def test_generate_int_range(self, capsys):
        """Test integer in specific range."""
        args = argparse.Namespace(count=10, min=50, max=60)
        result = gen_tool.cmd_int(args)
        assert result == 0
        captured = capsys.readouterr()
        for line in captured.out.strip().split("\n"):
            n = int(line)
            assert 50 <= n <= 60


class TestCmdFloat:
    """Tests for cmd_float function."""

    def test_generate_float(self, capsys):
        """Test generating random float."""
        args = argparse.Namespace(count=1, min=0.0, max=1.0, precision=2)
        result = gen_tool.cmd_float(args)
        assert result == 0
        captured = capsys.readouterr()
        f = float(captured.out.strip())
        assert 0.0 <= f <= 1.0


class TestCmdTimestamp:
    """Tests for cmd_timestamp function."""

    def test_timestamp_iso(self, capsys):
        """Test ISO timestamp."""
        args = argparse.Namespace(format="iso", custom=None)
        result = gen_tool.cmd_timestamp(args)
        assert result == 0
        captured = capsys.readouterr()
        # Should contain T separator and timezone
        assert "T" in captured.out

    def test_timestamp_unix(self, capsys):
        """Test Unix timestamp."""
        args = argparse.Namespace(format="unix", custom=None)
        result = gen_tool.cmd_timestamp(args)
        assert result == 0
        captured = capsys.readouterr()
        ts = int(captured.out.strip())
        assert ts > 0


class TestCmdChoice:
    """Tests for cmd_choice function."""

    def test_choice(self, capsys):
        """Test random choice."""
        args = argparse.Namespace(options=["red", "green", "blue"], count=1)
        result = gen_tool.cmd_choice(args)
        assert result == 0
        captured = capsys.readouterr()
        choice = captured.out.strip()
        assert choice in ["red", "green", "blue"]


class TestCmdShuffle:
    """Tests for cmd_shuffle function."""

    def test_shuffle(self, temp_file, capsys):
        """Test shuffling lines."""
        path = temp_file("a\nb\nc\nd\ne")
        args = argparse.Namespace(file=str(path))
        result = gen_tool.cmd_shuffle(args)
        assert result == 0
        captured = capsys.readouterr()
        lines = set(captured.out.strip().split("\n"))
        assert lines == {"a", "b", "c", "d", "e"}


class TestCmdSample:
    """Tests for cmd_sample function."""

    def test_sample(self, temp_file, capsys):
        """Test sampling lines."""
        path = temp_file("a\nb\nc\nd\ne\nf\ng\nh\ni\nj")
        args = argparse.Namespace(file=str(path), n=3)
        result = gen_tool.cmd_sample(args)
        assert result == 0
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert len(lines) == 3
