"""Shared fixtures for script tests."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_file(temp_dir):
    """Create a temporary file with content."""
    def _create(content: str, name: str = "test.txt"):
        path = temp_dir / name
        path.write_text(content)
        return path
    return _create


@pytest.fixture
def capture_stdout(monkeypatch):
    """Capture stdout for testing."""
    from io import StringIO
    buffer = StringIO()
    monkeypatch.setattr(sys, "stdout", buffer)
    return buffer


@pytest.fixture
def capture_stderr(monkeypatch):
    """Capture stderr for testing."""
    from io import StringIO
    buffer = StringIO()
    monkeypatch.setattr(sys, "stderr", buffer)
    return buffer
