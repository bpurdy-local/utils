"""Tests for setup.py (development setup script)."""

import argparse
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Import the script module with alias to avoid conflict
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import setup as setup_script


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_project_root(self):
        """Test getting project root."""
        root = setup_script.get_project_root()
        assert root.is_dir()


class TestCheckPythonVersion:
    """Tests for check_python_version function."""

    def test_python_version(self, capsys):
        """Test checking Python version."""
        # This should pass since we're running with Python 3.11+
        result = setup_script.check_python_version()
        assert result is True
        captured = capsys.readouterr()
        assert "Python" in captured.out


class TestCheckUvInstalled:
    """Tests for check_uv_installed function."""

    @patch("subprocess.run")
    def test_uv_installed(self, mock_run, capsys):
        """Test when uv is installed."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=b"uv 0.5.0"
        )
        result = setup_script.check_uv_installed()
        assert result is True

    @patch("subprocess.run")
    def test_uv_not_installed(self, mock_run, capsys):
        """Test when uv is not installed."""
        mock_run.return_value = MagicMock(returncode=127)
        result = setup_script.check_uv_installed()
        assert result is False


class TestRunStep:
    """Tests for run_step function."""

    @patch("subprocess.run")
    def test_run_step_success(self, mock_run, capsys):
        """Test successful step."""
        mock_run.return_value = MagicMock(returncode=0)
        result = setup_script.run_step("Test step", ["echo", "test"])
        assert result is True
        captured = capsys.readouterr()
        assert "Done" in captured.out

    @patch("subprocess.run")
    def test_run_step_failure(self, mock_run, capsys):
        """Test failed step."""
        mock_run.return_value = MagicMock(returncode=1)
        result = setup_script.run_step("Test step", ["false"])
        assert result is False
        captured = capsys.readouterr()
        assert "Failed" in captured.out
