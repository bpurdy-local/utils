#!/usr/bin/env python3
"""Run linting and formatting tools."""

import argparse
import subprocess
import sys
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Terminal


def get_project_root() -> PathLib:
    """Get the project root directory."""
    return PathLib(__file__).parent.parent


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{Terminal.colorize(description, color='cyan', bold=True)}")
    Terminal.print_line("─", width=60)

    result = subprocess.run(cmd, cwd=get_project_root())
    success = result.returncode == 0

    if success:
        print(Terminal.colorize("✓ Passed", color="green"))
    else:
        print(Terminal.colorize("✗ Failed", color="red"))

    return success


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run linting, formatting, and type checking tools.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all checks (format, lint, type check)
  python lint.py

  # Run all checks on a specific path
  python lint.py utils/

  # Check formatting without modifying files
  python lint.py --check

  # Auto-fix linting issues
  python lint.py --fix

  # Only run the formatter
  python lint.py --format

  # Only run type checking
  python lint.py --types

  # Fix linting issues in specific file
  python lint.py --fix --lint utils/string.py

Output:
  ┌────────────────────────────────┐
  │ Running Code Quality Checks    │
  └────────────────────────────────┘

  Formatting code (ruff format)
  ────────────────────────────────
  ✓ Passed

  Linting code (ruff check)
  ────────────────────────────────
  ✓ Passed

  ════════════════════════════════
  All checks passed!
""",
    )
    parser.add_argument(
        "--fix", "-f",
        action="store_true",
        help="auto-fix linting issues where possible",
    )
    parser.add_argument(
        "--check", "-c",
        action="store_true",
        help="check formatting only, don't modify files",
    )
    parser.add_argument(
        "--format",
        action="store_true",
        help="only run the formatter (ruff format)",
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="only run the linter (ruff check)",
    )
    parser.add_argument(
        "--types",
        action="store_true",
        help="only run the type checker (pyright)",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="path to check (default: current directory)",
    )
    args = parser.parse_args()

    Terminal.print_box("Running Code Quality Checks")

    all_passed = True
    run_all = not (args.format or args.lint or args.types)

    # Ruff format
    if run_all or args.format:
        if args.check:
            cmd = ["ruff", "format", "--check", args.path]
            desc = "Checking formatting (ruff format --check)"
        else:
            cmd = ["ruff", "format", args.path]
            desc = "Formatting code (ruff format)"
        if not run_command(cmd, desc):
            all_passed = False

    # Ruff lint
    if run_all or args.lint:
        cmd = ["ruff", "check", args.path]
        if args.fix:
            cmd.append("--fix")
            desc = "Linting code with fixes (ruff check --fix)"
        else:
            desc = "Linting code (ruff check)"
        if not run_command(cmd, desc):
            all_passed = False

    # Type checking
    if run_all or args.types:
        cmd = ["pyright", args.path]
        desc = "Type checking (pyright)"
        if not run_command(cmd, desc):
            all_passed = False

    # Summary
    print()
    Terminal.print_line("═", width=60)
    if all_passed:
        print(Terminal.colorize("All checks passed!", color="green", bold=True))
        return 0
    else:
        print(Terminal.colorize("Some checks failed!", color="red", bold=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
