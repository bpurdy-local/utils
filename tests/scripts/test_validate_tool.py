"""Tests for validate_tool.py."""

import argparse
import sys
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import validate_tool


class TestCmdEmail:
    """Tests for cmd_email function."""

    def test_valid_email(self, capsys):
        """Test validating valid email."""
        args = argparse.Namespace(
            value="user@example.com",
            file=None,
            verbose=False,
        )
        result = validate_tool.cmd_email(args)
        assert result == 0

    def test_invalid_email(self, capsys):
        """Test validating invalid email."""
        args = argparse.Namespace(
            value="not-an-email",
            file=None,
            verbose=False,
        )
        result = validate_tool.cmd_email(args)
        assert result == 1


class TestCmdUrl:
    """Tests for cmd_url function."""

    def test_valid_url(self, capsys):
        """Test validating valid URL."""
        args = argparse.Namespace(
            value="https://example.com",
            file=None,
            verbose=False,
        )
        result = validate_tool.cmd_url(args)
        assert result == 0

    def test_invalid_url(self, capsys):
        """Test validating invalid URL."""
        args = argparse.Namespace(
            value="not-a-url",
            file=None,
            verbose=False,
        )
        result = validate_tool.cmd_url(args)
        assert result == 1


class TestCmdIp:
    """Tests for cmd_ip function."""

    def test_valid_ipv4(self, capsys):
        """Test validating valid IPv4."""
        args = argparse.Namespace(
            value="192.168.1.1",
            file=None,
            v4=False,
            v6=False,
            verbose=False,
        )
        result = validate_tool.cmd_ip(args)
        assert result == 0

    def test_valid_ipv6(self, capsys):
        """Test validating valid IPv6."""
        args = argparse.Namespace(
            value="2001:db8::1",
            file=None,
            v4=False,
            v6=False,
            verbose=False,
        )
        result = validate_tool.cmd_ip(args)
        assert result == 0

    def test_invalid_ip(self, capsys):
        """Test validating invalid IP."""
        args = argparse.Namespace(
            value="999.999.999.999",
            file=None,
            v4=False,
            v6=False,
            verbose=False,
        )
        result = validate_tool.cmd_ip(args)
        assert result == 1

    def test_ipv4_only(self, capsys):
        """Test IPv4 only validation."""
        args = argparse.Namespace(
            value="2001:db8::1",  # IPv6 should fail
            file=None,
            v4=True,
            v6=False,
            verbose=False,
        )
        result = validate_tool.cmd_ip(args)
        assert result == 1


class TestCmdUuid:
    """Tests for cmd_uuid function."""

    def test_valid_uuid(self, capsys):
        """Test validating valid UUID."""
        args = argparse.Namespace(
            value="550e8400-e29b-41d4-a716-446655440000",
            file=None,
            verbose=False,
        )
        result = validate_tool.cmd_uuid(args)
        assert result == 0

    def test_invalid_uuid(self, capsys):
        """Test validating invalid UUID."""
        args = argparse.Namespace(
            value="not-a-uuid",
            file=None,
            verbose=False,
        )
        result = validate_tool.cmd_uuid(args)
        assert result == 1


class TestCmdJson:
    """Tests for cmd_json function."""

    def test_valid_json(self, capsys):
        """Test validating valid JSON."""
        args = argparse.Namespace(
            value='{"key": "value"}',
            file=None,
            schema=None,
            stats=False,
        )
        result = validate_tool.cmd_json(args)
        assert result == 0

    def test_invalid_json(self, capsys):
        """Test validating invalid JSON."""
        args = argparse.Namespace(
            value='{invalid}',
            file=None,
            schema=None,
            stats=False,
        )
        result = validate_tool.cmd_json(args)
        assert result == 1


class TestCmdRegex:
    """Tests for cmd_regex function."""

    def test_matching_pattern(self, capsys):
        """Test value matching pattern."""
        args = argparse.Namespace(
            pattern=r"^\d{5}$",
            value="12345",
            file=None,
            ignore_case=False,
            full=True,
            verbose=False,
        )
        result = validate_tool.cmd_regex(args)
        assert result == 0

    def test_non_matching_pattern(self, capsys):
        """Test value not matching pattern."""
        args = argparse.Namespace(
            pattern=r"^\d{5}$",
            value="1234",  # Only 4 digits
            file=None,
            ignore_case=False,
            full=True,
            verbose=False,
        )
        result = validate_tool.cmd_regex(args)
        assert result == 1


class TestCmdFile:
    """Tests for cmd_file function."""

    def test_file_exists(self, temp_file, capsys):
        """Test file exists."""
        path = temp_file("content")
        args = argparse.Namespace(
            path=str(path),
            is_file=False,
            is_dir=False,
            min_size=None,
            max_size=None,
            extension=None,
        )
        result = validate_tool.cmd_file(args)
        assert result == 0

    def test_file_not_exists(self, capsys):
        """Test file not exists."""
        args = argparse.Namespace(
            path="/nonexistent/file.txt",
            is_file=False,
            is_dir=False,
            min_size=None,
            max_size=None,
            extension=None,
        )
        result = validate_tool.cmd_file(args)
        assert result == 1

    def test_file_extension(self, temp_file, capsys):
        """Test file extension validation."""
        path = temp_file("content", name="test.json")
        args = argparse.Namespace(
            path=str(path),
            is_file=False,
            is_dir=False,
            min_size=None,
            max_size=None,
            extension="json",
        )
        result = validate_tool.cmd_file(args)
        assert result == 0
