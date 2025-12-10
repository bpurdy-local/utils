"""Tests for deps.py."""

import argparse
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import deps


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_project_root(self):
        """Test getting project root."""
        root = deps.get_project_root()
        assert root.is_dir()


class TestRunCommand:
    """Tests for run_command function."""

    @patch("subprocess.run")
    def test_run_command(self, mock_run, capsys):
        """Test running a command."""
        mock_run.return_value = MagicMock(returncode=0)
        result = deps.run_command(["echo", "test"], "Test command")
        assert result.returncode == 0
        captured = capsys.readouterr()
        assert "Test command" in captured.out

    @patch("subprocess.run")
    def test_run_command_capture(self, mock_run):
        """Test running a command with capture."""
        mock_run.return_value = MagicMock(returncode=0, stdout="output")
        result = deps.run_command(["echo", "test"], "Test", capture=True)
        assert result.returncode == 0
