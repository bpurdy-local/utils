"""Tests for watch.py."""

import argparse
import sys
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import watch


class TestGetFileHash:
    """Tests for get_file_hash function."""

    def test_hash_file(self, temp_file):
        """Test hashing a file."""
        path = temp_file("test content")
        result = watch.get_file_hash(Path(path))
        assert len(result) == 32  # MD5 hex digest

    def test_hash_same_content(self, temp_file):
        """Test same content produces same hash."""
        path1 = temp_file("identical content", name="file1.txt")
        path2 = temp_file("identical content", name="file2.txt")
        hash1 = watch.get_file_hash(Path(path1))
        hash2 = watch.get_file_hash(Path(path2))
        assert hash1 == hash2

    def test_hash_different_content(self, temp_file):
        """Test different content produces different hash."""
        path1 = temp_file("content 1", name="file1.txt")
        path2 = temp_file("content 2", name="file2.txt")
        hash1 = watch.get_file_hash(Path(path1))
        hash2 = watch.get_file_hash(Path(path2))
        assert hash1 != hash2

    def test_hash_nonexistent(self, temp_dir):
        """Test hashing nonexistent file returns empty string."""
        result = watch.get_file_hash(temp_dir / "nonexistent.txt")
        assert result == ""


class TestGetFiles:
    """Tests for get_files function."""

    def test_get_all_files(self, temp_dir):
        """Test getting all files."""
        (temp_dir / "file1.txt").write_text("content1")
        (temp_dir / "file2.txt").write_text("content2")

        files = watch.get_files(temp_dir)
        assert len(files) == 2

    def test_get_files_with_pattern(self, temp_dir):
        """Test getting files with pattern."""
        (temp_dir / "file1.py").write_text("python")
        (temp_dir / "file2.txt").write_text("text")

        files = watch.get_files(temp_dir, patterns=["*.py"])
        assert len(files) == 1
        assert any("file1.py" in str(f) for f in files.keys())

    def test_get_files_with_exclude(self, temp_dir):
        """Test getting files with exclude pattern."""
        (temp_dir / "keep.py").write_text("keep")
        (temp_dir / "exclude.log").write_text("exclude")

        files = watch.get_files(temp_dir, exclude=["*.log"])
        assert len(files) == 1
        assert any("keep.py" in str(f) for f in files.keys())

    def test_get_files_recursive(self, temp_dir):
        """Test recursive file discovery."""
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        (temp_dir / "root.txt").write_text("root")
        (subdir / "nested.txt").write_text("nested")

        files = watch.get_files(temp_dir, recursive=True)
        assert len(files) == 2

    def test_get_files_non_recursive(self, temp_dir):
        """Test non-recursive file discovery."""
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        (temp_dir / "root.txt").write_text("root")
        (subdir / "nested.txt").write_text("nested")

        files = watch.get_files(temp_dir, recursive=False)
        assert len(files) == 1


class TestRunCommand:
    """Tests for run_command function."""

    def test_run_command(self, capsys):
        """Test running a command."""
        result = watch.run_command("echo hello")
        assert result == 0

    def test_run_command_with_substitution(self, capsys, temp_file):
        """Test running command with file substitution."""
        path = temp_file("content")
        result = watch.run_command(f"echo {{}}", Path(path))
        assert result == 0
