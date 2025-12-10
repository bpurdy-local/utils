"""Tests for lint.py."""

import argparse
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import lint


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_project_root(self):
        """Test getting project root."""
        root = lint.get_project_root()
        assert root.is_dir()


class TestRunCommand:
    """Tests for run_command function."""

    @patch("subprocess.run")
    def test_run_command_success(self, mock_run, capsys):
        """Test successful command."""
        mock_run.return_value = MagicMock(returncode=0)
        result = lint.run_command(["echo", "test"], "Test command")
        assert result is True
        captured = capsys.readouterr()
        assert "Test command" in captured.out
        assert "Passed" in captured.out

    @patch("subprocess.run")
    def test_run_command_failure(self, mock_run, capsys):
        """Test failed command."""
        mock_run.return_value = MagicMock(returncode=1)
        result = lint.run_command(["false"], "Failing command")
        assert result is False
        captured = capsys.readouterr()
        assert "Failed" in captured.out
