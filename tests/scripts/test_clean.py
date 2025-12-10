"""Tests for clean.py."""

import argparse
import sys
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import clean


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_project_root(self):
        """Test getting project root."""
        root = clean.get_project_root()
        assert root.is_dir()
        assert (root / "scripts").is_dir()


class TestFindAndRemoveDirs:
    """Tests for find_and_remove_dirs function."""

    def test_find_dirs_dry_run(self, temp_dir, capsys):
        """Test finding directories in dry run mode."""
        cache_dir = temp_dir / "__pycache__"
        cache_dir.mkdir()

        count = clean.find_and_remove_dirs(temp_dir, ["__pycache__"], dry_run=True)
        assert count == 1
        assert cache_dir.exists()  # Should not be deleted in dry run
        captured = capsys.readouterr()
        assert "Would remove" in captured.out

    def test_find_dirs_remove(self, temp_dir, capsys):
        """Test removing directories."""
        cache_dir = temp_dir / "__pycache__"
        cache_dir.mkdir()

        count = clean.find_and_remove_dirs(temp_dir, ["__pycache__"], dry_run=False)
        assert count == 1
        assert not cache_dir.exists()

    def test_find_dirs_pattern(self, temp_dir):
        """Test finding directories with pattern."""
        egg_dir = temp_dir / "mypackage.egg-info"
        egg_dir.mkdir()

        count = clean.find_and_remove_dirs(temp_dir, ["*.egg-info"], dry_run=True)
        assert count == 1


class TestFindAndRemoveFiles:
    """Tests for find_and_remove_files function."""

    def test_find_files_dry_run(self, temp_dir, capsys):
        """Test finding files in dry run mode."""
        pyc_file = temp_dir / "test.pyc"
        pyc_file.write_text("")

        count = clean.find_and_remove_files(temp_dir, ["*.pyc"], dry_run=True)
        assert count == 1
        assert pyc_file.exists()
        captured = capsys.readouterr()
        assert "Would remove" in captured.out

    def test_find_files_remove(self, temp_dir, capsys):
        """Test removing files."""
        pyc_file = temp_dir / "test.pyc"
        pyc_file.write_text("")

        count = clean.find_and_remove_files(temp_dir, ["*.pyc"], dry_run=False)
        assert count == 1
        assert not pyc_file.exists()

    def test_excludes_venv(self, temp_dir):
        """Test that .venv is excluded."""
        venv_dir = temp_dir / ".venv"
        venv_dir.mkdir()
        pyc_file = venv_dir / "test.pyc"
        pyc_file.write_text("")

        count = clean.find_and_remove_files(temp_dir, ["*.pyc"], dry_run=False)
        assert count == 0  # Should not find files in .venv
        assert pyc_file.exists()
