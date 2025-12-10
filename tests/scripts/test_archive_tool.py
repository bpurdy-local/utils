"""Tests for archive_tool.py."""

import argparse
import os
import sys
import zipfile
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import archive_tool


class TestGetArchiveType:
    """Tests for get_archive_type function."""

    def test_zip(self):
        """Test zip detection."""
        assert archive_tool.get_archive_type("test.zip") == "zip"

    def test_tar_gz(self):
        """Test tar.gz detection."""
        assert archive_tool.get_archive_type("test.tar.gz") == "tar.gz"
        assert archive_tool.get_archive_type("test.tgz") == "tar.gz"

    def test_tar_bz2(self):
        """Test tar.bz2 detection."""
        assert archive_tool.get_archive_type("test.tar.bz2") == "tar.bz2"
        assert archive_tool.get_archive_type("test.tbz2") == "tar.bz2"

    def test_tar(self):
        """Test tar detection."""
        assert archive_tool.get_archive_type("test.tar") == "tar"

    def test_gz(self):
        """Test gz detection."""
        assert archive_tool.get_archive_type("test.gz") == "gz"

    def test_unknown(self):
        """Test unknown type."""
        assert archive_tool.get_archive_type("test.xyz") == "unknown"


class TestFormatSize:
    """Tests for format_size function."""

    def test_bytes(self):
        """Test bytes formatting."""
        result = archive_tool.format_size(500)
        assert "B" in result

    def test_kilobytes(self):
        """Test kilobytes formatting."""
        result = archive_tool.format_size(2048)
        assert "KB" in result

    def test_megabytes(self):
        """Test megabytes formatting."""
        result = archive_tool.format_size(2 * 1024 * 1024)
        assert "MB" in result


class TestCmdCreate:
    """Tests for cmd_create function."""

    def test_create_zip(self, temp_dir, temp_file, capsys):
        """Test creating zip archive."""
        # Create test file
        test_file = temp_file("test content", name="test.txt")
        output_zip = temp_dir / "test.zip"

        args = argparse.Namespace(
            output=str(output_zip),
            files=[str(test_file)],
            type=None,
        )
        result = archive_tool.cmd_create(args)
        assert result == 0
        assert output_zip.exists()

        # Verify contents
        with zipfile.ZipFile(output_zip, "r") as zf:
            assert "test.txt" in zf.namelist()


class TestCmdList:
    """Tests for cmd_list function."""

    def test_list_zip(self, temp_dir, temp_file, capsys):
        """Test listing zip contents."""
        # Create test zip
        test_file = temp_file("test content", name="test.txt")
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.write(test_file, "test.txt")

        args = argparse.Namespace(archive=str(zip_path))
        result = archive_tool.cmd_list(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "test.txt" in captured.out


class TestCmdTest:
    """Tests for cmd_test function."""

    def test_valid_zip(self, temp_dir, temp_file, capsys):
        """Test testing valid zip."""
        # Create test zip
        test_file = temp_file("test content", name="test.txt")
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.write(test_file, "test.txt")

        args = argparse.Namespace(archive=str(zip_path))
        result = archive_tool.cmd_test(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "OK" in captured.out


class TestCmdExtract:
    """Tests for cmd_extract function."""

    def test_extract_zip(self, temp_dir, temp_file, capsys):
        """Test extracting zip archive."""
        # Create test zip
        test_file = temp_file("test content", name="test.txt")
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.write(test_file, "test.txt")

        # Extract
        extract_dir = temp_dir / "extracted"
        args = argparse.Namespace(
            archive=str(zip_path),
            output=str(extract_dir),
        )
        result = archive_tool.cmd_extract(args)
        assert result == 0
        assert (extract_dir / "test.txt").exists()
