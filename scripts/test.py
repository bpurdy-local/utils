#!/usr/bin/env python3
"""Run tests with various options."""

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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run tests with pytest, with convenient options for common workflows.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests (excludes slow tests by default)
  python test.py

  # Run tests in a specific file
  python test.py tests/test_string.py

  # Run tests matching a keyword
  python test.py -k "truncate"
  # Output: Only runs tests with "truncate" in the name

  # Run with coverage report
  python test.py --cov
  # Output: Shows coverage percentages in terminal

  # Generate HTML coverage report
  python test.py --html
  # Output: Creates htmlcov/index.html

  # Stop on first failure (useful for debugging)
  python test.py -x -v

  # Re-run only failed tests from last run
  python test.py --lf

  # Run tests in parallel (faster)
  python test.py -n 4

  # Watch mode - auto-rerun on file changes
  python test.py --watch

  # Include slow tests
  python test.py --slow

  # Combine options
  python test.py tests/test_string.py -v -x --cov

Output:
  ════════════════════════════════
  Tests passed!
""",
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="specific test file or directory to run",
    )
    parser.add_argument(
        "-k", "--keyword",
        help="only run tests matching keyword expression (e.g., 'test_truncate')",
    )
    parser.add_argument(
        "-m", "--marker",
        help="only run tests with given marker (e.g., 'slow', 'integration')",
    )
    parser.add_argument(
        "--cov",
        action="store_true",
        help="run with coverage report in terminal",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="generate HTML coverage report in htmlcov/",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="verbose output with test names",
    )
    parser.add_argument(
        "-x", "--exitfirst",
        action="store_true",
        help="exit immediately on first failure",
    )
    parser.add_argument(
        "--lf", "--last-failed",
        action="store_true",
        help="re-run only tests that failed last time",
    )
    parser.add_argument(
        "-n", "--numprocesses",
        type=int,
        help="run tests in parallel with N processes",
    )
    parser.add_argument(
        "--watch", "-w",
        action="store_true",
        help="watch for file changes and auto-rerun tests",
    )
    parser.add_argument(
        "--slow",
        action="store_true",
        help="include slow tests (excluded by default)",
    )
    args = parser.parse_args()

    Terminal.print_box("Running Tests")

    # Build pytest command
    cmd = ["pytest"]

    # Add path if specified
    if args.path:
        cmd.append(args.path)

    # Keyword filter
    if args.keyword:
        cmd.extend(["-k", args.keyword])

    # Marker filter
    if args.marker:
        cmd.extend(["-m", args.marker])
    elif not args.slow:
        # Exclude slow tests by default
        cmd.extend(["-m", "not slow"])

    # Coverage
    if args.cov or args.html:
        cmd.extend(["--cov=utils", "--cov-report=term-missing"])
        if args.html:
            cmd.append("--cov-report=html")

    # Verbose
    if args.verbose:
        cmd.append("-v")

    # Exit on first failure
    if args.exitfirst:
        cmd.append("-x")

    # Last failed
    if args.lf:
        cmd.append("--lf")

    # Parallel
    if args.numprocesses:
        cmd.extend(["-n", str(args.numprocesses)])

    # Watch mode
    if args.watch:
        cmd = ["ptw", "--"] + cmd[1:]  # Replace pytest with pytest-watch

    print(f"\n{Terminal.colorize('Command:', color='cyan')} {' '.join(cmd)}")
    Terminal.print_line("─", width=60)
    print()

    result = subprocess.run(cmd, cwd=get_project_root())

    print()
    Terminal.print_line("═", width=60)

    if result.returncode == 0:
        print(Terminal.colorize("Tests passed!", color="green", bold=True))
    else:
        print(Terminal.colorize("Tests failed!", color="red", bold=True))

    if args.html and result.returncode == 0:
        print(f"\n{Terminal.colorize('Coverage report:', color='cyan')} htmlcov/index.html")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
