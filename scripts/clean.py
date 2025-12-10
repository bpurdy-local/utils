#!/usr/bin/env python3
"""Clean build artifacts, caches, and temporary files."""

import argparse
import subprocess
import sys
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Path, Terminal

# Directories to clean
CACHE_DIRS = [
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".pyright",
    "*.egg-info",
    ".eggs",
    "dist",
    "build",
    "htmlcov",
    ".tox",
    ".nox",
]

# File patterns to clean
FILE_PATTERNS = [
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".coverage",
    ".coverage.*",
    "coverage.xml",
    "*.cover",
    "*.log",
    ".DS_Store",
]


def get_project_root() -> PathLib:
    """Get the project root directory."""
    return PathLib(__file__).parent.parent


def find_and_remove_dirs(root: PathLib, patterns: list[str], dry_run: bool = False) -> int:
    """Find and remove directories matching patterns."""
    count = 0
    for pattern in patterns:
        for path in root.rglob(pattern):
            if path.is_dir() and ".venv" not in str(path):
                if dry_run:
                    print(f"  Would remove: {path}")
                else:
                    print(f"  {Terminal.colorize('Removing:', color='yellow')} {path}")
                    Path.rm(str(path), recursive=True)
                count += 1
    return count


def find_and_remove_files(root: PathLib, patterns: list[str], dry_run: bool = False) -> int:
    """Find and remove files matching patterns."""
    count = 0
    for pattern in patterns:
        for path in root.rglob(pattern):
            if path.is_file() and ".venv" not in str(path):
                if dry_run:
                    print(f"  Would remove: {path}")
                else:
                    print(f"  {Terminal.colorize('Removing:', color='yellow')} {path}")
                    path.unlink()
                count += 1
    return count


def clean_pip_cache(dry_run: bool = False) -> None:
    """Clean pip cache."""
    if dry_run:
        print("  Would clean pip cache")
        return
    print(f"  {Terminal.colorize('Cleaning pip cache...', color='cyan')}")
    subprocess.run([sys.executable, "-m", "pip", "cache", "purge"], capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Clean build artifacts, caches, and temporary files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what would be deleted (safe to run)
  python clean.py --dry-run

  # Clean all build artifacts and caches
  python clean.py

  # Clean everything including pip cache
  python clean.py --all

  # Just clean pip cache too
  python clean.py --pip-cache

What gets cleaned:
  Directories: __pycache__, .pytest_cache, .mypy_cache, .ruff_cache,
               dist/, build/, htmlcov/, *.egg-info, .eggs, .tox, .nox
  Files:       *.pyc, *.pyo, .coverage, coverage.xml, *.log, .DS_Store

Output:
  Removed 15 directories and 42 files
""",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="show what would be deleted without actually deleting",
    )
    parser.add_argument(
        "--pip-cache",
        action="store_true",
        help="also purge the pip cache directory",
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="clean everything including pip cache",
    )
    args = parser.parse_args()

    root = get_project_root()

    if args.dry_run:
        print(Terminal.colorize("DRY RUN - No files will be deleted", color="yellow", bold=True))

    Terminal.print_box(f"Cleaning project: {root}")
    print()

    print(Terminal.colorize("Cleaning directories...", color="cyan", bold=True))
    dir_count = find_and_remove_dirs(root, CACHE_DIRS, args.dry_run)

    print()
    print(Terminal.colorize("Cleaning files...", color="cyan", bold=True))
    file_count = find_and_remove_files(root, FILE_PATTERNS, args.dry_run)

    if args.pip_cache or args.all:
        print()
        print(Terminal.colorize("Cleaning pip cache...", color="cyan", bold=True))
        clean_pip_cache(args.dry_run)

    print()
    Terminal.print_line("─")
    action = "Would remove" if args.dry_run else "Removed"
    result = f"{action} {dir_count} directories and {file_count} files"
    print(Terminal.colorize(result, color="green", bold=True))

    return 0


if __name__ == "__main__":
    sys.exit(main())
