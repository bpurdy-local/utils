"""Tests for git_tool.py."""

import argparse
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import git_tool


class TestRunGit:
    """Tests for run_git function."""

    def test_run_git_success(self):
        """Test successful git command."""
        code, stdout, stderr = git_tool.run_git(["--version"])
        assert code == 0
        assert "git version" in stdout

    def test_run_git_failure(self):
        """Test failed git command."""
        code, stdout, stderr = git_tool.run_git(["invalid-command"])
        assert code != 0


class TestCmdBranches:
    """Tests for cmd_branches function."""

    @patch("git_tool.run_git")
    def test_branches(self, mock_run_git, capsys):
        """Test listing branches."""
        mock_run_git.side_effect = [
            (0, "main|2 hours ago|John|Initial commit", ""),
            (0, "main", ""),
        ]
        args = argparse.Namespace(limit=20, verbose=False)
        result = git_tool.cmd_branches(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "main" in captured.out


class TestCmdCleanup:
    """Tests for cmd_cleanup function."""

    @patch("git_tool.run_git")
    def test_cleanup_no_branches(self, mock_run_git, capsys):
        """Test cleanup with no merged branches."""
        mock_run_git.side_effect = [
            (0, "* main", ""),  # merged branches
            (0, "main", ""),    # current branch
        ]
        args = argparse.Namespace(dry_run=False, force=True)
        result = git_tool.cmd_cleanup(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "No branches to clean" in captured.out

    @patch("git_tool.run_git")
    def test_cleanup_dry_run(self, mock_run_git, capsys):
        """Test cleanup dry run."""
        mock_run_git.side_effect = [
            (0, "* main\n  feature-x", ""),
            (0, "main", ""),
        ]
        args = argparse.Namespace(dry_run=True, force=False)
        result = git_tool.cmd_cleanup(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Dry run" in captured.out


class TestCmdStats:
    """Tests for cmd_stats function."""

    @patch("git_tool.run_git")
    def test_stats(self, mock_run_git, capsys):
        """Test repository statistics."""
        mock_run_git.side_effect = [
            (0, "100", ""),       # total commits
            (0, "10\tJohn\n5\tJane", ""),  # contributors
            (0, "2022-01-01", ""),  # first commit
            (0, "2024-01-01", ""),  # last commit
            (0, "file1.py\nfile2.py", ""),  # files
            (0, "main\nfeature", ""),  # branches
            (0, "v1.0\nv1.1", ""),  # tags
        ]
        args = argparse.Namespace(verbose=False)
        result = git_tool.cmd_stats(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Total commits" in captured.out
        assert "Contributors" in captured.out


class TestCmdRecent:
    """Tests for cmd_recent function."""

    @patch("git_tool.run_git")
    def test_recent(self, mock_run_git, capsys):
        """Test recently modified files."""
        mock_run_git.return_value = (
            0,
            "file1.py\nfile2.py\nfile1.py\nfile3.py",
            "",
        )
        args = argparse.Namespace(commits=50, limit=20)
        result = git_tool.cmd_recent(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "file1.py" in captured.out


class TestCmdStashList:
    """Tests for cmd_stash_list function."""

    @patch("git_tool.run_git")
    def test_stash_list_empty(self, mock_run_git, capsys):
        """Test empty stash list."""
        mock_run_git.return_value = (0, "", "")
        args = argparse.Namespace()
        result = git_tool.cmd_stash_list(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "No stashes" in captured.out

    @patch("git_tool.run_git")
    def test_stash_list_with_stashes(self, mock_run_git, capsys):
        """Test stash list with entries."""
        mock_run_git.return_value = (
            0,
            "stash@{0}|WIP on main|2 hours ago",
            "",
        )
        args = argparse.Namespace()
        result = git_tool.cmd_stash_list(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "stash@{0}" in captured.out


class TestCmdAlias:
    """Tests for cmd_alias function."""

    @patch("git_tool.run_git")
    def test_alias_list_empty(self, mock_run_git, capsys):
        """Test listing aliases when none exist."""
        mock_run_git.return_value = (1, "", "")
        args = argparse.Namespace(name=None, command=None)
        result = git_tool.cmd_alias(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "No aliases" in captured.out

    @patch("git_tool.run_git")
    def test_alias_list(self, mock_run_git, capsys):
        """Test listing aliases."""
        mock_run_git.return_value = (
            0,
            "alias.st status\nalias.co checkout",
            "",
        )
        args = argparse.Namespace(name=None, command=None)
        result = git_tool.cmd_alias(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "st" in captured.out
        assert "co" in captured.out
