#!/usr/bin/env python3
"""Bump version and prepare release."""

import argparse
import re
import subprocess
import sys
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Path, Terminal


def get_project_root() -> PathLib:
    """Get the project root directory."""
    return PathLib(__file__).parent.parent


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    pyproject_path = get_project_root() / "pyproject.toml"
    content = Path.read(str(pyproject_path))

    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if match:
        return match.group(1)
    raise ValueError("Could not find version in pyproject.toml")


def bump_version(current: str, bump_type: str) -> str:
    """Bump version based on type (major, minor, patch)."""
    parts = current.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {current}")

    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

    return f"{major}.{minor}.{patch}"


def update_version_in_file(file_path: PathLib, old_version: str, new_version: str) -> bool:
    """Update version in a file. Returns True if file was updated."""
    if not file_path.exists():
        return False

    content = Path.read(str(file_path))
    if old_version in content:
        new_content = content.replace(old_version, new_version)
        Path.write(str(file_path), content=new_content)
        return True
    return False


def run_checks() -> bool:
    """Run pre-release checks."""
    print(Terminal.colorize("\nRunning pre-release checks...", color="cyan", bold=True))

    # Run tests
    print("\n  Running tests...")
    result = subprocess.run(
        ["pytest", "-x", "-q"],
        cwd=get_project_root(),
        capture_output=True,
    )
    if result.returncode != 0:
        print(Terminal.colorize("  ✗ Tests failed!", color="red"))
        return False
    print(Terminal.colorize("  ✓ Tests passed", color="green"))

    # Run linting
    print("\n  Running linter...")
    result = subprocess.run(
        ["ruff", "check", "."],
        cwd=get_project_root(),
        capture_output=True,
    )
    if result.returncode != 0:
        print(Terminal.colorize("  ✗ Linting failed!", color="red"))
        return False
    print(Terminal.colorize("  ✓ Linting passed", color="green"))

    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bump version and prepare a release with git commit and optional tag.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what would happen (no changes made)
  python release.py patch --dry-run
  # Output:
  #   Current version: 1.2.3
  #   New version: 1.2.4
  #   DRY RUN - No changes will be made

  # Bump patch version (1.2.3 -> 1.2.4)
  python release.py patch

  # Bump minor version (1.2.3 -> 1.3.0)
  python release.py minor

  # Bump major version (1.2.3 -> 2.0.0)
  python release.py major

  # Create release with git tag
  python release.py patch --tag
  # Output: Creates tag v1.2.4

  # Skip running tests and linting
  python release.py patch --skip-checks

Version types:
  patch  - Bug fixes, backwards compatible (1.2.3 -> 1.2.4)
  minor  - New features, backwards compatible (1.2.3 -> 1.3.0)
  major  - Breaking changes (1.2.3 -> 2.0.0)

What it does:
  1. Runs tests and linting (unless --skip-checks)
  2. Updates version in pyproject.toml and __init__.py
  3. Creates git commit "chore: bump version to X.Y.Z"
  4. Optionally creates git tag vX.Y.Z
""",
    )
    parser.add_argument(
        "bump_type",
        choices=["major", "minor", "patch"],
        help="version bump type (major/minor/patch)",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="show what would be done without making changes",
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="skip running tests and linting before release",
    )
    parser.add_argument(
        "--tag", "-t",
        action="store_true",
        help="create a git tag (e.g., v1.2.3)",
    )
    args = parser.parse_args()

    Terminal.print_box("Release Preparation")

    # Get current version
    try:
        current_version = get_current_version()
    except ValueError as e:
        print(Terminal.colorize(f"Error: {e}", color="red"))
        return 1

    new_version = bump_version(current_version, args.bump_type)

    print(f"\n{Terminal.colorize('Current version:', color='cyan')} {current_version}")
    print(f"{Terminal.colorize('New version:', color='green')} {new_version}")
    print(f"{Terminal.colorize('Bump type:', color='cyan')} {args.bump_type}")

    if args.dry_run:
        print(Terminal.colorize("\nDRY RUN - No changes will be made", color="yellow", bold=True))
        return 0

    # Run checks
    if not args.skip_checks:
        if not run_checks():
            print(Terminal.colorize("\nRelease aborted due to failed checks.", color="red"))
            return 1

    # Confirm
    print()
    if not Terminal.confirm(f"Bump version to {new_version}?", default=False):
        print("Release cancelled.")
        return 0

    # Update version in files
    print(Terminal.colorize("\nUpdating version...", color="cyan", bold=True))

    root = get_project_root()
    files_to_update = [
        root / "pyproject.toml",
        root / "utils" / "__init__.py",
    ]

    for file_path in files_to_update:
        if update_version_in_file(file_path, current_version, new_version):
            print(f"  Updated: {file_path.name}")

    # Create git commit
    print(Terminal.colorize("\nCreating git commit...", color="cyan", bold=True))
    subprocess.run(["git", "add", "-A"], cwd=root)
    subprocess.run(
        ["git", "commit", "-m", f"chore: bump version to {new_version}"],
        cwd=root,
    )

    # Create git tag if requested
    if args.tag:
        print(Terminal.colorize("\nCreating git tag...", color="cyan", bold=True))
        subprocess.run(["git", "tag", f"v{new_version}"], cwd=root)
        print(f"  Created tag: v{new_version}")

    print()
    Terminal.print_line("═", width=60)
    print(Terminal.colorize(f"Released version {new_version}!", color="green", bold=True))

    if args.tag:
        print(f"\nDon't forget to push the tag: git push origin v{new_version}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
