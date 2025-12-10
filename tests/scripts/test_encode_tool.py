"""Tests for encode_tool.py."""

import argparse
import sys
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import encode_tool


class TestBase64:
    """Tests for base64 encode/decode."""

    def test_base64_encode(self, capsys):
        """Test base64 encoding."""
        args = argparse.Namespace(
            text="Hello World",
            file=None,
            output=None,
        )
        result = encode_tool.cmd_base64_encode(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "SGVsbG8gV29ybGQ=" in captured.out

    def test_base64_decode(self, capsys):
        """Test base64 decoding."""
        args = argparse.Namespace(
            text="SGVsbG8gV29ybGQ=",
            file=None,
            output=None,
        )
        result = encode_tool.cmd_base64_decode(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Hello World" in captured.out


class TestUrlEncode:
    """Tests for URL encode/decode."""

    def test_url_encode(self, capsys):
        """Test URL encoding."""
        args = argparse.Namespace(
            text="hello world & stuff",
            file=None,
            output=None,
        )
        result = encode_tool.cmd_url_encode(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "hello%20world" in captured.out or "hello+world" in captured.out

    def test_url_decode(self, capsys):
        """Test URL decoding."""
        args = argparse.Namespace(
            text="hello%20world",
            file=None,
            output=None,
        )
        result = encode_tool.cmd_url_decode(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "hello world" in captured.out


class TestHtmlEncode:
    """Tests for HTML encode/decode."""

    def test_html_encode(self, capsys):
        """Test HTML encoding."""
        args = argparse.Namespace(
            text="<script>alert('xss')</script>",
            file=None,
            output=None,
        )
        result = encode_tool.cmd_html_encode(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "&lt;script&gt;" in captured.out

    def test_html_decode(self, capsys):
        """Test HTML decoding."""
        args = argparse.Namespace(
            text="&lt;p&gt;text&lt;/p&gt;",
            file=None,
            output=None,
        )
        result = encode_tool.cmd_html_decode(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "<p>text</p>" in captured.out


class TestDefangFang:
    """Tests for defang/fang operations."""

    def test_defang_url(self, capsys):
        """Test defanging URLs."""
        args = argparse.Namespace(
            text="https://malicious.com",
            file=None,
            output=None,
        )
        result = encode_tool.cmd_defang(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "hxxps" in captured.out or "[.]" in captured.out

    def test_defang_ip(self, capsys):
        """Test defanging IP addresses."""
        args = argparse.Namespace(
            text="192.168.1.1",
            file=None,
            output=None,
        )
        result = encode_tool.cmd_defang(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "[.]" in captured.out

    def test_fang(self, capsys):
        """Test refanging."""
        args = argparse.Namespace(
            text="hxxps://example[.]com",
            file=None,
            output=None,
        )
        result = encode_tool.cmd_fang(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "https://example.com" in captured.out


class TestHash:
    """Tests for hashing functions."""

    def test_hash_md5(self, capsys):
        """Test MD5 hashing."""
        args = argparse.Namespace(
            text="test",
            file=None,
            algorithm="md5",
            output=None,
        )
        result = encode_tool.cmd_hash(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "098f6bcd4621d373cade4e832627b4f6" in captured.out

    def test_hash_sha256(self, capsys):
        """Test SHA256 hashing."""
        args = argparse.Namespace(
            text="test",
            file=None,
            algorithm="sha256",
            output=None,
        )
        result = encode_tool.cmd_hash(args)
        assert result == 0
        captured = capsys.readouterr()
        # SHA256 of "test" starts with "9f86d08..."
        assert captured.out.strip().startswith("9f86d08")


class TestVerify:
    """Tests for hash verification."""

    def test_verify_valid(self, capsys):
        """Test verifying valid hash."""
        # SHA256 of "test" - the default algorithm
        args = argparse.Namespace(
            file="test",
            hash="9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
        )
        result = encode_tool.cmd_verify(args)
        assert result == 0

    def test_verify_invalid(self, capsys):
        """Test verifying invalid hash."""
        args = argparse.Namespace(
            file="test",
            hash="invalidhash",
        )
        result = encode_tool.cmd_verify(args)
        assert result == 1
