"""Tests for test.py (the test runner script)."""

import argparse
import sys
from pathlib import Path

import pytest

# Import the script module with alias to avoid conflict with test framework
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import test as test_script


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_project_root(self):
        """Test getting project root."""
        root = test_script.get_project_root()
        assert root.is_dir()
        assert (root / "tests").is_dir()
