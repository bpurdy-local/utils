#!/usr/bin/env python3
"""Watch files for changes and run commands."""

import argparse
import fnmatch
import hashlib
import subprocess
import sys
import time
from pathlib import Path as PathLib

# Add parent directory to path to import utils
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils import Terminal


def get_file_hash(path: PathLib) -> str:
    """Get hash of file contents."""
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except Exception:
        return ""


def get_files(
    directory: PathLib,
    patterns: list[str] | None = None,
    exclude: list[str] | None = None,
    recursive: bool = True,
) -> dict[PathLib, str]:
    """Get files and their hashes."""
    files = {}
    exclude = exclude or []

    if recursive:
        all_files = directory.rglob("*")
    else:
        all_files = directory.glob("*")

    for path in all_files:
        if not path.is_file():
            continue

        # Check exclude patterns
        rel_path = str(path.relative_to(directory))
        skip = False
        for ex in exclude:
            if fnmatch.fnmatch(rel_path, ex) or fnmatch.fnmatch(path.name, ex):
                skip = True
                break
        if skip:
            continue

        # Check include patterns
        if patterns:
            match = False
            for pat in patterns:
                if fnmatch.fnmatch(rel_path, pat) or fnmatch.fnmatch(path.name, pat):
                    match = True
                    break
            if not match:
                continue

        files[path] = get_file_hash(path)

    return files


def run_command(cmd: str, changed_file: PathLib | None = None) -> int:
    """Run command with optional file substitution."""
    if changed_file and "{}" in cmd:
        cmd = cmd.replace("{}", str(changed_file))

    print(Terminal.colorize(f"\n$ {cmd}", color="cyan"))
    Terminal.print_line("─", width=60)

    result = subprocess.run(cmd, shell=True)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Watch files for changes and run commands automatically.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Watch current directory and run tests on any change
  python watch.py "pytest"

  # Watch for Python file changes only
  python watch.py "pytest" -p "*.py"

  # Watch multiple patterns
  python watch.py "npm run build" -p "*.ts" -p "*.tsx" -p "*.css"

  # Watch specific directory
  python watch.py "make" -d src/

  # Run command with changed filename ({} is replaced)
  python watch.py "python {}" -p "*.py"
  # When test.py changes: runs "python test.py"

  # Exclude patterns
  python watch.py "npm test" -e "*.log" -e "dist/*"

  # Run command immediately on start
  python watch.py "pytest" --initial

  # Clear screen before each run
  python watch.py "go build" --clear

  # Custom check interval (default 1 second)
  python watch.py "cargo test" -i 0.5

  # Custom debounce time (default 0.5 seconds)
  python watch.py "npm run build" --debounce 1.0

  # Typical workflows:
  python watch.py "pytest tests/" -p "*.py"      # Python testing
  python watch.py "npm run build" -p "*.ts"      # TypeScript build
  python watch.py "cargo check" -p "*.rs"        # Rust check

Default excludes: *.pyc, __pycache__, .git, .venv, node_modules, *.swp, *.log
""",
    )
    parser.add_argument("command", help="Command to run (use {} for changed file)")
    parser.add_argument("-d", "--directory", default=".", help="Directory to watch")
    parser.add_argument("-p", "--pattern", action="append", help="File patterns to watch")
    parser.add_argument("-e", "--exclude", action="append", help="Patterns to exclude")
    parser.add_argument("-i", "--interval", type=float, default=1.0, help="Check interval (seconds)")
    parser.add_argument("--no-recursive", action="store_true", help="Don't watch subdirectories")
    parser.add_argument("--initial", action="store_true", help="Run command initially")
    parser.add_argument("--clear", action="store_true", help="Clear screen before each run")
    parser.add_argument("--debounce", type=float, default=0.5, help="Debounce time (seconds)")
    args = parser.parse_args()

    directory = PathLib(args.directory).resolve()
    if not directory.is_dir():
        print(Terminal.colorize(f"Not a directory: {args.directory}", color="red"))
        return 1

    # Default patterns
    patterns = args.pattern or ["*"]
    exclude = args.exclude or [
        "*.pyc", "__pycache__", ".git", ".venv", "node_modules",
        "*.swp", "*.swo", ".DS_Store", "*.log"
    ]

    print(Terminal.colorize(f"Watching: {directory}", color="cyan", bold=True))
    print(f"Patterns: {', '.join(patterns)}")
    print(f"Exclude: {', '.join(exclude)}")
    print(f"Command: {args.command}")
    print()
    print(Terminal.colorize("Press Ctrl+C to stop", color="yellow"))
    Terminal.print_line("═", width=60)

    # Initial file state
    file_hashes = get_files(directory, patterns, exclude, not args.no_recursive)
    print(f"Watching {len(file_hashes)} files")

    # Run initially if requested
    if args.initial:
        run_command(args.command)

    last_run = 0

    try:
        while True:
            time.sleep(args.interval)

            # Check for changes
            new_hashes = get_files(directory, patterns, exclude, not args.no_recursive)

            changed = []
            added = []
            removed = []

            # Find changed and added files
            for path, hash_val in new_hashes.items():
                if path not in file_hashes:
                    added.append(path)
                elif file_hashes[path] != hash_val:
                    changed.append(path)

            # Find removed files
            for path in file_hashes:
                if path not in new_hashes:
                    removed.append(path)

            # Update state
            file_hashes = new_hashes

            # Process changes
            all_changes = changed + added + removed
            if all_changes:
                # Debounce
                now = time.time()
                if now - last_run < args.debounce:
                    continue
                last_run = now

                if args.clear:
                    Terminal.clear()

                # Report changes
                for path in added:
                    print(Terminal.colorize(f"+ {path.relative_to(directory)}", color="green"))
                for path in changed:
                    print(Terminal.colorize(f"~ {path.relative_to(directory)}", color="yellow"))
                for path in removed:
                    print(Terminal.colorize(f"- {path.relative_to(directory)}", color="red"))

                # Run command
                first_change = changed[0] if changed else (added[0] if added else None)
                run_command(args.command, first_change)

    except KeyboardInterrupt:
        print(Terminal.colorize("\n\nStopped watching", color="yellow"))
        return 0


if __name__ == "__main__":
    sys.exit(main())
