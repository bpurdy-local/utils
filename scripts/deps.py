#!/usr/bin/env python3
"""Manage project dependencies."""

import argparse
import subprocess
import sys
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Path, Terminal


def get_project_root() -> PathLib:
    """Get the project root directory."""
    return PathLib(__file__).parent.parent


def run_command(cmd: list[str], description: str, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a command with nice output."""
    print(f"\n{Terminal.colorize(description, color='cyan', bold=True)}")
    Terminal.print_line("─", width=60)

    if capture:
        return subprocess.run(cmd, cwd=get_project_root(), capture_output=True, text=True)
    return subprocess.run(cmd, cwd=get_project_root())


def install_deps(dev: bool = False, extras: list[str] | None = None) -> int:
    """Install dependencies."""
    cmd = ["uv", "pip", "install", "-e", "."]

    if dev:
        cmd[-1] = "-e.[dev]"
    elif extras:
        extras_str = ",".join(extras)
        cmd[-1] = f"-e.[{extras_str}]"

    result = run_command(cmd, "Installing dependencies")
    return result.returncode


def update_deps() -> int:
    """Update all dependencies."""
    result = run_command(
        ["uv", "pip", "install", "--upgrade", "-e", ".[dev]"],
        "Updating dependencies",
    )
    return result.returncode


def list_deps(outdated: bool = False) -> int:
    """List dependencies."""
    if outdated:
        result = run_command(
            ["uv", "pip", "list", "--outdated"],
            "Outdated dependencies",
        )
    else:
        result = run_command(
            ["uv", "pip", "list"],
            "Installed dependencies",
        )
    return result.returncode


def show_tree() -> int:
    """Show dependency tree."""
    result = run_command(
        ["uv", "pip", "tree"],
        "Dependency tree",
    )
    return result.returncode


def export_requirements(output: str = "requirements.txt", dev: bool = False) -> int:
    """Export dependencies to requirements.txt."""
    result = run_command(
        ["uv", "pip", "freeze"],
        f"Exporting to {output}",
        capture=True,
    )

    if result.returncode == 0:
        Path.write(str(get_project_root() / output), content=result.stdout)
        print(Terminal.colorize(f"\nExported to {output}", color="green"))

    return result.returncode


def audit_deps() -> int:
    """Audit dependencies for security vulnerabilities."""
    # Try pip-audit first
    result = subprocess.run(
        ["pip-audit"],
        cwd=get_project_root(),
        capture_output=True,
    )

    if result.returncode == 127:  # Command not found
        print(Terminal.colorize("pip-audit not installed.", color="yellow"))
        print("Install with: pip install pip-audit")
        return 1

    run_command(["pip-audit"], "Security audit")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manage project dependencies using uv.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Install production dependencies
  python deps.py install

  # Install with dev dependencies
  python deps.py install --dev

  # Install specific extras
  python deps.py install --extras datetime

  # Update all dependencies to latest versions
  python deps.py update

  # List all installed packages
  python deps.py list
  # Output:
  #   requests    2.31.0
  #   pydantic    2.5.0
  #   ...

  # Show only outdated packages
  python deps.py list --outdated
  # Output:
  #   Package    Current  Latest
  #   requests   2.31.0   2.32.0

  # Show dependency tree
  python deps.py tree
  # Output:
  #   requests 2.31.0
  #   ├── certifi
  #   └── urllib3

  # Export to requirements.txt
  python deps.py export
  python deps.py export -o requirements-dev.txt

  # Check for security vulnerabilities
  python deps.py audit
""",
    )
    subparsers = parser.add_subparsers(dest="command", help="command to run")

    # Install command
    p = subparsers.add_parser("install", help="install project dependencies")
    p.add_argument("--dev", "-d", action="store_true", help="include dev dependencies")
    p.add_argument("--extras", "-e", nargs="+", help="extra dependency groups to install")

    # Update command
    subparsers.add_parser("update", help="update all dependencies to latest versions")

    # List command
    p = subparsers.add_parser("list", help="list installed dependencies")
    p.add_argument("--outdated", "-o", action="store_true", help="show only outdated packages")

    # Tree command
    subparsers.add_parser("tree", help="show dependency tree with nested dependencies")

    # Export command
    p = subparsers.add_parser("export", help="export dependencies to requirements.txt")
    p.add_argument("--output", "-o", default="requirements.txt", help="output filename")
    p.add_argument("--dev", "-d", action="store_true", help="include dev dependencies")

    # Audit command
    subparsers.add_parser("audit", help="audit dependencies for security vulnerabilities")

    args = parser.parse_args()

    Terminal.print_box("Dependency Management")

    if args.command == "install":
        return install_deps(args.dev, args.extras)
    elif args.command == "update":
        return update_deps()
    elif args.command == "list":
        return list_deps(args.outdated)
    elif args.command == "tree":
        return show_tree()
    elif args.command == "export":
        return export_requirements(args.output, args.dev)
    elif args.command == "audit":
        return audit_deps()
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
