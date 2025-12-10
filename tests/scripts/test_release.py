"""Tests for release.py."""

import argparse
import sys
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import release


class TestGetProjectRoot:
    """Tests for get_project_root function."""

    def test_project_root(self):
        """Test getting project root."""
        root = release.get_project_root()
        assert root.is_dir()


class TestBumpVersion:
    """Tests for bump_version function."""

    def test_bump_patch(self):
        """Test patch version bump."""
        result = release.bump_version("1.2.3", "patch")
        assert result == "1.2.4"

    def test_bump_minor(self):
        """Test minor version bump."""
        result = release.bump_version("1.2.3", "minor")
        assert result == "1.3.0"

    def test_bump_major(self):
        """Test major version bump."""
        result = release.bump_version("1.2.3", "major")
        assert result == "2.0.0"

    def test_bump_from_zero(self):
        """Test bumping from zero."""
        result = release.bump_version("0.0.1", "patch")
        assert result == "0.0.2"

    def test_invalid_version(self):
        """Test invalid version format."""
        with pytest.raises(ValueError):
            release.bump_version("1.2", "patch")

    def test_invalid_bump_type(self):
        """Test invalid bump type."""
        with pytest.raises(ValueError):
            release.bump_version("1.2.3", "invalid")


class TestGetCurrentVersion:
    """Tests for get_current_version function."""

    def test_get_version(self):
        """Test getting current version."""
        version = release.get_current_version()
        # Should be a valid version string
        parts = version.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)


class TestUpdateVersionInFile:
    """Tests for update_version_in_file function."""

    def test_update_version(self, temp_file):
        """Test updating version in file."""
        path = temp_file('version = "1.0.0"\nname = "test"')
        result = release.update_version_in_file(Path(path), "1.0.0", "1.0.1")
        assert result is True

        content = Path(path).read_text()
        assert "1.0.1" in content
        assert "1.0.0" not in content

    def test_update_version_not_found(self, temp_file):
        """Test updating when version not in file."""
        path = temp_file('name = "test"')
        result = release.update_version_in_file(Path(path), "1.0.0", "1.0.1")
        assert result is False

    def test_update_nonexistent_file(self, temp_dir):
        """Test updating nonexistent file."""
        result = release.update_version_in_file(
            temp_dir / "nonexistent.txt",
            "1.0.0",
            "1.0.1"
        )
        assert result is False
