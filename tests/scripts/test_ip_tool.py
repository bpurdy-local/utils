"""Tests for ip_tool.py."""

import argparse
import sys
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import ip_tool


class TestCmdInfo:
    """Tests for cmd_info function."""

    def test_ipv4_public(self, capsys):
        """Test public IPv4 info."""
        args = argparse.Namespace(ip="8.8.8.8")
        result = ip_tool.cmd_info(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "IPv4" in captured.out
        assert "Public" in captured.out

    def test_ipv4_private(self, capsys):
        """Test private IPv4 info."""
        args = argparse.Namespace(ip="192.168.1.1")
        result = ip_tool.cmd_info(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Private" in captured.out

    def test_loopback(self, capsys):
        """Test loopback IP."""
        args = argparse.Namespace(ip="127.0.0.1")
        result = ip_tool.cmd_info(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Loopback: True" in captured.out

    def test_invalid_ip(self, capsys):
        """Test invalid IP."""
        args = argparse.Namespace(ip="not-an-ip")
        result = ip_tool.cmd_info(args)
        # Should try to resolve as hostname, likely fail
        assert result == 1


class TestCmdResolve:
    """Tests for cmd_resolve function."""

    def test_resolve_localhost(self, capsys):
        """Test resolving localhost."""
        args = argparse.Namespace(hostname="localhost", all=False)
        result = ip_tool.cmd_resolve(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "127.0.0.1" in captured.out


class TestCmdCidr:
    """Tests for cmd_cidr function."""

    def test_cidr_24(self, capsys):
        """Test /24 CIDR calculation."""
        args = argparse.Namespace(
            cidr="192.168.1.0/24",
            list_hosts=False,
        )
        result = ip_tool.cmd_cidr(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "192.168.1.0" in captured.out
        assert "255.255.255.0" in captured.out
        assert "254" in captured.out  # usable hosts

    def test_cidr_16(self, capsys):
        """Test /16 CIDR calculation."""
        args = argparse.Namespace(
            cidr="10.0.0.0/16",
            list_hosts=False,
        )
        result = ip_tool.cmd_cidr(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "10.0.0.0" in captured.out
        assert "255.255.0.0" in captured.out

    def test_invalid_cidr(self, capsys):
        """Test invalid CIDR."""
        args = argparse.Namespace(
            cidr="invalid",
            list_hosts=False,
        )
        result = ip_tool.cmd_cidr(args)
        assert result == 1


class TestCmdPort:
    """Tests for cmd_port function."""

    def test_port_closed(self, capsys):
        """Test checking closed port."""
        # Port 59999 is unlikely to be open
        args = argparse.Namespace(
            host="127.0.0.1",
            ports=[59999],
            timeout=1.0,
        )
        result = ip_tool.cmd_port(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "closed" in captured.out
