"""Tests for diff_tool.py."""

import argparse
import sys
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import diff_tool


class TestReadLines:
    """Tests for read_lines function."""

    def test_read_lines(self, temp_file):
        """Test reading lines from file."""
        path = temp_file("line1\nline2\nline3")
        lines = diff_tool.read_lines(str(path))
        assert len(lines) == 3


class TestCmdFiles:
    """Tests for cmd_files function."""

    def test_identical_files(self, temp_file, capsys):
        """Test comparing identical files."""
        path1 = temp_file("same content", name="file1.txt")
        path2 = temp_file("same content", name="file2.txt")
        args = argparse.Namespace(
            file1=str(path1),
            file2=str(path2),
            unified=False,
            format="unified",
            context=3,
            color=False,
        )
        result = diff_tool.cmd_files(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "identical" in captured.out.lower()

    def test_different_files(self, temp_file, capsys):
        """Test comparing different files."""
        path1 = temp_file("line1\nline2\n", name="file1.txt")
        path2 = temp_file("line1\nchanged\n", name="file2.txt")
        args = argparse.Namespace(
            file1=str(path1),
            file2=str(path2),
            unified=True,
            format="unified",
            context=3,
            color=False,
        )
        result = diff_tool.cmd_files(args)
        assert result == 1  # Returns 1 when files differ
        captured = capsys.readouterr()
        assert "-line2" in captured.out or "- line2" in captured.out


class TestCmdDirs:
    """Tests for cmd_dirs function."""

    def test_identical_dirs(self, temp_dir, capsys):
        """Test comparing identical directories."""
        dir1 = temp_dir / "dir1"
        dir2 = temp_dir / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        (dir1 / "file.txt").write_text("content")
        (dir2 / "file.txt").write_text("content")

        args = argparse.Namespace(
            dir1=str(dir1),
            dir2=str(dir2),
            content=False,
        )
        result = diff_tool.cmd_dirs(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "identical" in captured.out.lower()

    def test_different_dirs(self, temp_dir, capsys):
        """Test comparing directories with different files."""
        dir1 = temp_dir / "dir1"
        dir2 = temp_dir / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        (dir1 / "only_in_1.txt").write_text("content")
        (dir2 / "only_in_2.txt").write_text("content")

        args = argparse.Namespace(
            dir1=str(dir1),
            dir2=str(dir2),
            content=False,
        )
        result = diff_tool.cmd_dirs(args)
        assert result == 1
        captured = capsys.readouterr()
        assert "only_in_1.txt" in captured.out
        assert "only_in_2.txt" in captured.out


class TestCmdStats:
    """Tests for cmd_stats function."""

    def test_stats(self, temp_file, capsys):
        """Test diff statistics."""
        path1 = temp_file("line1\nline2\nline3\n", name="file1.txt")
        path2 = temp_file("line1\nchanged\nline3\nnew\n", name="file2.txt")
        args = argparse.Namespace(
            file1=str(path1),
            file2=str(path2),
        )
        result = diff_tool.cmd_stats(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "additions" in captured.out
        assert "deletions" in captured.out
        assert "Similarity" in captured.out
