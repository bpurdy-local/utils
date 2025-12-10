"""Tests for serve.py."""

import argparse
import sys
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import serve


class TestFindFreePort:
    """Tests for find_free_port function."""

    def test_find_port(self):
        """Test finding a free port."""
        # Port 0 tells OS to assign any free port
        port = serve.find_free_port(8000)
        assert port >= 8000
        assert port < 8100

    def test_find_port_on_localhost(self):
        """Test finding port on localhost."""
        port = serve.find_free_port(9000, "localhost")
        assert port >= 9000


class TestCustomHandler:
    """Tests for CustomHandler class."""

    def test_format_size_bytes(self):
        """Test formatting bytes."""
        handler = serve.CustomHandler.__new__(serve.CustomHandler)
        result = handler._format_size(500)
        assert "B" in result

    def test_format_size_kilobytes(self):
        """Test formatting kilobytes."""
        handler = serve.CustomHandler.__new__(serve.CustomHandler)
        result = handler._format_size(2048)
        assert "KB" in result

    def test_format_size_megabytes(self):
        """Test formatting megabytes."""
        handler = serve.CustomHandler.__new__(serve.CustomHandler)
        result = handler._format_size(2 * 1024 * 1024)
        assert "MB" in result

    def test_format_size_gigabytes(self):
        """Test formatting gigabytes."""
        handler = serve.CustomHandler.__new__(serve.CustomHandler)
        result = handler._format_size(2 * 1024 * 1024 * 1024)
        assert "GB" in result
